from app import app, mongo
from flask import render_template

from flask import request, jsonify
from flask import Response
from flask_pymongo import pymongo

import messageParser

import json, bson
from bson import json_util
import datetime
import dateutil.parser

from error_handler import InvalidUsage
import json_serialhelper

import gevent
import numpy as np

from datetime import timedelta, datetime
from flask import make_response, request, current_app
from functools import update_wrapper

import time

import mongo_operations as mongo_ops


def getitem(obj, item, default):
    # Cool idea found in https://github.com/bokeh/bokeh/blob/master/examples/embed/simple/simple.py
    if item not in obj:
        return default
    else:
        return obj[item]


def convertToIsoDate(obj, key="createdOn"):
    """ Recursive function to change a string embedded in dictionary to datetime.dateime object.
        The default key is 'createdOn'
        Examples of dictionaries:
        {'createdOn':{'$gte':'2016-03-02', '$lt':'2015-03-02'}}
        {'createdOn':'2015-03-02'}
        {'createdOn':1}
        {'$sort':{'userAccount':1,'createdOn':1}}
    """

    # if i not in ['createdOn', 'lastUpdated', '$lt', '$gte']:
    # continue
    if isinstance(obj, dict):
        for i in obj.keys():
            obj[i] = convertToIsoDate(obj[i], key=i)
    else:
        try:
            if key in [
                "createdOn",
                "lastUpdated",
                "$lt",
                "$gte",
            ]:  # only try to convert for this keys
                obj = dateutil.parser.parse(obj)
        except:
            pass
    return obj


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def index():
    return "Welcome to mxdb server."


@app.route("/db/insert", methods=["PUT"])
def dbInsert():
    """
        Usage: <server>/db/insert?collection=<Datasets|MergeState....>
        where collection specifies collection in MongoDB

        Alternative usage: <server>/db/insert
        where {collection:<Datasets|MergeState....>}

        Note: 'collection' given in the URL overwrites the one in the message body

        General remarks:
        - messages is send in the message body as JSON
    """

    import dbCollections

    collections = dbCollections.dbCollections()
    outmsg = {}

    message = request.json
    if message == {} or message is None:
        raise InvalidUsage("No message given in the request body")

    # Optional arguments as key-values in the URL
    options = request.args.to_dict()

    # Collection should be given in the URL arguments or message body
    collection = options.pop("collection", None)
    if collection is None:
        collection = message.pop("collection", None)

    if collection is None:
        err_msg = (
            "Collection not specified. It can be\
        specified in the request URL as ?collection=<value>, or in\
        the message body {collection:<value>}. Allowed <values>: %s"
            % collections
        )
        raise InvalidUsage(err_msg)

    # Test if collection is valid and ensure proper capitalization
    try:
        collection = collections.collectionTypeParser()[collection.lower()]
    except KeyError:
        err_msg = (
            "Wrong collection given: (%s).\
               It must be one of the following: %s"
            % (collection, collections)
        )
        raise InvalidUsage(err_msg)

    # Parse message and create metadata
    try:
        parsedMessage = messageParser.messageParser(message)
        if collection.lower() not in ["vdp"]:
            parsedMessage.gen_metadata()
    except Exception as e:
        err_msg = "Cannot parse incoming message. Reason: {}".format(e)
        raise InvalidUsage(err_msg)

    # Special inserts go here
    if collection == "Eiger":
        # Compose funcname = {insertEiger(message)| insertStream(message)}
        funcName = "insert" + collection + "(message)"
        outmsg = eval(funcName)  # run the function
        return jsonify(outmsg)  # return

    # Insert message
    try:
        # iid = mongo.db[collection].insert_one(parsedMessage).inserted_id
        iid = mongo_ops.insert_one(collection, parsedMessage)
        outmsg["status"] = "OK"
        outmsg[u"insertID"] = str(iid)
    except mongo_ops.MongoNotConnected:
        raise InvalidUsage("Could not connect to MongoDB server", 403)
    except pymongo.errors.DuplicateKeyError:
        raise InvalidUsage("message with this _id already exists in database ")

    return jsonify(outmsg)


def insertEiger(message):
    """
    Inserts to
    - collection EigerMask - holds binary mask pickled(bzip2(numpy.ndarray))
    - collection Eiger - mask data and reference to binary file where actual mask is stored
    """

    import bz2, cPickle
    from base64 import b64decode
    from bson.binary import Binary
    import numpy as np
    import sys

    outmsg = {}
    coll = message["msgtype"]
    collMask = coll + "Mask"

    outmsg[coll] = u"%s" % ("OK",)  # innocent until found guilty
    mask = message["value"]["data"]
    mask_decode = b64decode(mask)
    mask_decode = np.fromstring(mask_decode, dtype=message["value"]["type"]).reshape(
        message["value"]["shape"]
    )

    mask2db = bz2.compress(mask_decode)
    mask2db = cPickle.dumps(mask2db)
    mask2db = Binary(mask2db, subtype=128)

    messageMask = dict(data=mask2db)

    # FIXME: add dbParser to check for createdOn
    messageMask["createdOn"] = message["createdOn"]

    try:
        iid = mongo.db[collMask].insert_one(messageMask).inserted_id
    except Exception as e:
        msg = "Cannot insert document with Eiger binary mask. "
        raise InvalidUsage(msg + str(e))

    # Store refrence to binary mask
    message["value"]["data"] = iid
    # Insert mask data
    try:
        iid = mongo.db[coll].insert_one(message).inserted_id
        outmsg[u"insertID"] = str(iid)
    except Exception as e:
        msg = "Cannot insert document with Eiger mask data. "
        raise InvalidUsage(msg + str(e))

    return outmsg
