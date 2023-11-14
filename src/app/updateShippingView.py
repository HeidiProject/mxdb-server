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

import mongo_operations as mongo_ops


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/db/updateShipping", methods=["POST"])
def dbUpdateShipping():
    # cannot use pymongo.update_one() with nested dictionary
    # as it will replace whole contents, instead adding new key.
    # Need to go with dot notation 'results.fast_xds3={bla bla}
    """
    message format:
        {update_id: id, status: shipping_status,
         timestamp: datetime.datetime.now().isoformat()}

    additional keys that are not required:
    {
     }
    """
    import dbCollections
    import bson
    import ast

    # Check if message exists in the body of the request
    message = request.json
    if message == {} or message is None:
        raise InvalidUsage("No message given in the request body")

    collections = dbCollections.dbCollections()

    # Before anything check if the collection is given.
    try:
        collection = message.pop("collection")
    except KeyError:
        raise InvalidUsage(
            "Collection not specified in the input. Needs to be one of {}".format(
                collections.collectionNames()
            )
        )

    # Do checks for consistency
    requiredKeys = [u"msg_id", u"status", u"timestamp"]
    allowedStatus = [u"incoming", u"arrived", u"returning"]

    allowedCollections = [collections.Shipping]
    outmsg = {}

    if collection not in allowedCollections:
        raise InvalidUsage(
            "Wrong collection name. Collection needs to be one of {}. I got: {}".format(
                allowedCollections, collection
            )
        )

    # message = request.args.to_dict()
    keys = message.keys()

    if keys == []:
        raise InvalidUsage("updateShipping: got empty message.")

    for k in requiredKeys:
        if k not in keys:
            msg = 'Key: "%s" not found. It needs to be specified in URL' % k
            raise InvalidUsage(msg)

    try:
        timestamp = dateutil.parser.parse(message[u"timestamp"])
    except (ValueError, AttributeError):
        msg = "Wrong timestamp format. Use: datetime.datetime.now().isodate()"
        raise InvalidUsage(msg)

    status = message[u"status"]
    if status not in allowedStatus:
        allS = "".join([u"%s, " % s for s in allowedStatus])
        msg = 'Wrong status of Shipping: "%s". Allowed values: %s' % (
            status,
            allS,
        )
        raise InvalidUsage(msg)

    try:
        message[u"msg_id"] = bson.ObjectId(message[u"msg_id"])
    except Exception as e:
        msg = "Wrong ObjectID format: "
        raise InvalidUsage(msg + str(e))


    # Ready for update:
    query = dict(_id=message[u"msg_id"])
    update = {}

    status = message[u"status"]

    update[u"lastUpdated"] = timestamp

    dewarStatus = u"dewarStatus"
    update[dewarStatus] = status

    statusHistory = u"statusHistory.%s" % (status)
    update[statusHistory] = timestamp

    # Perform update
    try:
        result = mongo_ops.update_one(collection, query, update)
    except mongo_ops.MongoNotConnected:
        raise InvalidUsage("Could not connect to MongoDB server", 403)

    outmsg["status"] = "OK"
    outmsg["matched_count"] = result.matched_count
    outmsg["modified_count"] = result.modified_count
    outmsg["upserted_id"] = result.upserted_id

    if result.matched_count == 0:
        err_msg = "Did not update any documents"
        raise InvalidUsage(err_msg)

    return json.dumps(outmsg, default=json_serialhelper.json_serialhelper)
