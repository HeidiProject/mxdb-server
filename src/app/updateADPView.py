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


@app.route("/db/updateADP", methods=["POST"])
def dbUpdateADP():
    # cannot use pymongo.update_one() with nested dictionary
    # as it will replace whole contents, instead adding new key.
    # Need to go witj dot notation 'results.fast_xds3={bla bla}
    """
    message format:
        {update_id: id, adptype: adp_type, status: processin_status, 
         timestamp: datetime.datetime.now().isoformat()}

    addionial keys that are not required:
    {results: {stuff with resutls of processing},
     fqdn: dir location,
     adpinfo: statusMsgFromXDS,
     params: extra information stored in results.adp_type,
     angularrange: ang_range,
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
    # collection = collections.Adp

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
    requiredKeys = [u"msg_id", u"status", u"timestamp", "adptype"]
    allowedStatus = [u"pending", u"running", u"aborted", u"error", u"completed"]
    allowedAdpTypes = [
        "fast_xds_1",
        "fast_xds_2",
        "fast_xds_3",
        "gocom",
        "dials",
        "autoproc",
        "strategy",
        "gopy",
        "merging",
        "xia2dials",
    ]
    allowedCollections = [collections.Adp, collections.Merge]
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
        raise InvalidUsage("updateADP: got empty message.")

    for k in requiredKeys:
        if k not in keys:
            msg = 'Key: "%s" not found. It needs to be scpecified in URL' % k
            raise InvalidUsage(msg)

    try:
        timestamp = dateutil.parser.parse(message[u"timestamp"])
    except (ValueError, AttributeError):
        msg = "Wrong timestamp format. Use: datetime.datetime.now().isodate()"
        raise InvalidUsage(msg)

    status = message[u"status"]
    if status not in allowedStatus:
        allS = "".join([u"%s, " % s for s in allowedStatus])
        msg = 'Wrong status of Autoprocessing: "%s". Allowed values: %s' % (
            status,
            allS,
        )
        raise InvalidUsage(msg)

    adpType = message[u"adptype"]
    if adpType not in allowedAdpTypes:
        allT = "".join([u"%s, " % s for s in allowedAdpTypes])
        msg = 'Wrong Type of Autoprocessing: "%s". Allowed values: %s' % (adpType, allT)
        raise InvalidUsage(msg)

    try:
        message[u"msg_id"] = bson.ObjectId(message[u"msg_id"])
    except Exception as e:
        msg = "Wrong ObjectID format: "
        raise InvalidUsage(msg + str(e))

    ##########################################
    ## Check if optional parameters exists: ##
    ##########################################

    results = message.pop("results", None)
    fqdn = message.pop("fqdn", None)
    adpinfo = message.pop("adpinfo", None)
    angularrange = message.pop("angularrange", None)
    extraParams = message.pop("params", None)
    mergefolder = message.pop("mergefolder", None)
    ## Checking for optional paramters finished ##

    # Ready for update:
    query = dict(_id=message[u"msg_id"])
    update = {}

    adpType = message[u"adptype"]
    status = message[u"status"]
    # adpinfo = message[u'adpinfo']

    update[u"lastUpdated"] = timestamp

    adpStatus = u"adpStatus.%s" % adpType
    update[adpStatus] = status

    statusHistory = u"statusHistory.%s.%s" % (adpType, status)
    update[statusHistory] = timestamp

    # Include optional parameters in update
    if adpinfo != None:
        adpInfo = u"adpInfo.%s" % adpType
        update[adpInfo] = adpinfo

    if fqdn != None:
        FQDN = u"FQDN.%s" % adpType
        update[FQDN] = fqdn

    if angularrange != None:
        angularRange = u"angularRange.%s" % adpType
        update[angularRange] = angularrange

    if mergefolder != None:
        mergeFolder = u"mergeFolder"
        update[mergeFolder] = mergefolder

    if extraParams != None:
        paramsLabel = "%s_params" % adpType
        params = u"result.%s" % paramsLabel
        # try:
        #     extraParams = ast.literal_eval(extraParams)
        # except (ValueError, SyntaxError):
        #     err_msg = 'params needs to be a dictionary. Current value:', extraParams
        #     raise InvalidUsage(err_msg)
        update[params] = extraParams

    if results != None:
        result = u"result.%s" % adpType
        update[result] = results

    # Perform update
    # result = mongo.db[collection].update_one(query, {'$set':update})
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
