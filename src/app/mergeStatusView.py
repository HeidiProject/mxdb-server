#
# Set of routes controling updates to MargeState collection and CurrentMergeId
# Keeping it separate and not using universtal db/insert to have tight control
# If something goes wrong here, whole data processing goes wrong
#

from app import app, mongo

from flask import request, jsonify
from flask import Response
from flask_pymongo import pymongo
import messageParser

import json, bson

from error_handler import InvalidUsage
import json_serialhelper

import mongo_operations as mongo_ops


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/db/updateMergeCounter", methods=["POST"])
def updateMergeCounter():

    import dbCollections

    # Main message is send as a JSON in the message body
    try:
        message = request.json
    except:
        err_msg = "No message given in the request body"
        raise InvalidUsage(err_msg)

    # Optional arguments as key-values in the URL
    options = request.args.to_dict()

    try:
        parsedMessage = messageParser.messageParser(message)
    except Exception as e:
        err_msg = "Cannot parse incoming message. Reason: {}".format(e)
        raise InvalidUsage(err_msg)

    # Check is the message corresponds to the format of MergeStatus collection
    if not parsedMessage.valid_for_merge_status():
        err_msg = "Wrong format of the message. Allowed keys: {}".format(
            parsedMessage.merge_status_keys
        )
        raise InvalidUsage(err_msg)

    # Get proper collection name
    collection = dbCollections.dbCollections().MergeState

    # Construct the query and upsert the message to the database
    query = parsedMessage.copy()
    query.pop(
        "datasetCount"
    )  # remove datasetCount from query as this is the one we are increasing
    query.pop("lastUpdated")  # remove lastUpdated from the query
    query.pop("datasetList")  # remove datasetList from the query
    query.pop("datasetNumbers")  # remove datasetList from the query
    try:
        # result = mongo.db[collection].replace_one(query, parsedMessage, upsert=True)
        result = mongo_ops.replace_one(collection, query, parsedMessage, upsert=True)
    except mongo_ops.MongoNotConnected:
        raise InvalidUsage("Could not connect to MongoDB server", 403)
    except Exception as e:
        err_msg = "Error inserting document to database. Reason: {}".format(e)
        raise InvalidUsage(err_msg)

    return json.dumps(
        {
            "status": "OK",
            "message": None,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": result.upserted_id,
        },
        default=json_serialhelper.json_serialhelper,
    )


@app.route("/db/updateCurrentMergeId", methods=["POST"])
def updateCurrentMergeId():

    import dbCollections

    # Main message is send as a JSON in the message body
    try:
        message = request.json
    except:
        err_msg = "No message given in the request body"
        raise InvalidUsage(err_msg)

    # Optional arguments as key-values in the URL
    options = request.args.to_dict()

    try:
        parsedMessage = messageParser.messageParser(message)
    except Exception as e:
        err_msg = "Cannot parse incoming message. Reason: {}".format(e)
        raise InvalidUsage(err_msg)

    # Check is the message corresponds to the format of CurrentMergeId collection
    if not parsedMessage.valid_for_current_mergeId():
        err_msg = "Wrong format of the message or both mergeId and trackingId have value != None at the same time. Allowed keys: {}. Message I got: {}".format(
            parsedMessage.current_merge_id_keys, parsedMessage
        )
        raise InvalidUsage(err_msg)

    # Get proper collection name
    collection = dbCollections.dbCollections().CurrentMergeId

    # Create the query and upsert the message to the database
    query = parsedMessage.copy()
    query.pop("mergeId")
    query.pop("trackingId")
    query.pop("lastUpdated")
    query.pop("method")

    try:
        # result = mongo.db[collection].replace_one(query, parsedMessage, upsert=True)
        result = mongo_ops.replace_one(collection, query, parsedMessage, upsert=True)
    except mongo_ops.MongoNotConnected:
        raise InvalidUsage("Could not connect to MongoDB server", 403)
    except Exception as e:
        err_msg = "Error inserting document to database. Reason: {}".format(e)
        raise InvalidUsage(err_msg)

    return json.dumps(
        {
            "status": "OK",
            "message": None,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": result.upserted_id,
        },
        default=json_serialhelper.json_serialhelper,
    )


@app.route("/db/removeFromMergeState", methods=["POST"])
def removeFromMergeState():
    """
        Removes document from MergeState collection identified by
            {userAccount: String,
            beamline:     Strging,
            mergeId:      String,
            trackingId:   String}

        General remarks:
        - messages is send in the message body as JSON
    """
    import dbCollections

    collection = dbCollections.dbCollections().MergeState
    outmsg = {}

    # Main message is send as a JSON in the message body
    try:
        message = request.json
    except:
        err_msg = "No message given in the request body"
        raise InvalidUsage(err_msg)

    try:
        parsedMessage = messageParser.messageParser(message)
    except Exception as e:
        err_msg = "Cannot parse incoming message. Reason: {}".format(e)
        raise InvalidUsage(err_msg)

    # Check it the message has all the required keys to indetify document to be removed
    if not parsedMessage.valid_for_remove_from_merge_state():
        valid_keys = parsedMessage.valid_for_remove_from_merge_state_keys
        raise InvalidUsage(
            "Cannot parse dictionary. Did not find all the required keys: {}".format(
                valid_keys
            )
        )

    try:
        result = mongo_ops.delete_one(collection, parsedMessage)
    except mongo_ops.MongoNotConnected:
        raise InvalidUsage("Could not connect to MongoDB server", 403)

    outmsg["status"] = "OK"
    outmsg["deleted_count"] = result.deleted_count

    return json.dumps(outmsg, default=json_serialhelper.json_serialhelper)

    return jsonify(outmsg)


@app.route("/db/restoreMergeState", methods=["POST"])
def restoreMergeState():
    """Purges the whole MergeState collection for given beamline
        Input: {'beamline': 'x06sa', 
                'counter':[
                    {u'beamline': u'x06sa',
                    u'datasetCount': 11,
                    u'datasetList': {},
                    u'datasetNumbers': [],
                    u'lastUpdated': u'2017-11-23T20:47:51.667000+00:00',
                    u'mergeId': u'lyso5',
                    u'method': u'serial-xtal',
                    u'trackingId': u'e14eb79a-9a77-4d15-820e-e32ed98d697f',
                    u'userAccount': u'e15880'}]}
    """
    import dbCollections

    collection = dbCollections.dbCollections().MergeState
    outmsg = {}

    # Main message is send as a JSON in the message body
    try:
        message = request.json
    except:
        err_msg = "No message given in the request body"
        raise InvalidUsage(err_msg)

    try:
        parsedMessage = messageParser.messageParser(message)
    except Exception as e:
        err_msg = "Cannot parse incoming message. Reason: {}".format(e)
        raise InvalidUsage(err_msg)

    # Check it the message has all the required keys to indetify document to be removed
    if not parsedMessage.valid_for_restore_merge_state():
        valid_keys = parsedMessage.valid_for_restore_merge_state_keys
        raise InvalidUsage(
            "Cannot parse dictionary. Message sould have following keys: {}. I got: {}".format(
                valid_keys, parsedMessage
            )
        )

    beamline = parsedMessage["beamline"]
    counter = parsedMessage["counter"]

    purgeMsg = {"beamline": beamline}
    try:
        result = mongo_ops.delete_many(collection, purgeMsg)
    except mongo_ops.MongoNotConnected:
        raise InvalidUsage("Could not connect to MongoDB server", 403)

    # parse every message in the counter
    parsedCounter = []
    for item in counter:
        try:
            parsedMessage = messageParser.messageParser(item)
        except Exception as e:
            err_msg = "Cannot parse incoming message. Reason: {}".format(e)
            raise InvalidUsage(err_msg)

        if not parsedMessage.valid_for_merge_state():
            valid_keys = parsedMessage.valid_for_merge_state_keys
            raise InvalidUsage(
                "Cannot parse dictionary. Message sould have following keys: {}. I got: {}".format(
                    valid_keys, parsedMessage
                )
            )

        parsedCounter.append(parsedMessage)

    try:
        iids = mongo_ops.insert_many(collection, parsedCounter)
    except mongo_ops.MongoNotConnected:
        raise InvalidUsage("Could not connect to MongoDB server", 403)
    outmsg["status"] = "OK"
    outmsg["insertIds"] = list(iids)

    return json.dumps(outmsg, default=json_serialhelper.json_serialhelper)

    return jsonify(outmsg)
