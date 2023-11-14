from app import app, mongo

from flask import request, jsonify
from flask import Response
from flask_pymongo import pymongo

import messageParser

import json, bson
from bson import json_util
import datetime
import dateutil.parser

from flask_cors import CORS, cross_origin

from error_handler import InvalidUsage
import json_serialhelper
import mongo_operations as mongo_ops


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/db/countseen", methods=["POST"])
def countSeen():
    """
    Returns count of not seen datasets:
    input as args:
    user=user
    beamline=beamline
    after=isoformat with date

    """

    import dbCollections

    collections = dbCollections.dbCollections()
    outmsg = {}

    arguments = {}

    # Query can be either given as arguments or as json payload in the mesage body
    arguments_from_args = request.args.to_dict()
    arguments_from_payload = request.json

    arguments.update(arguments_from_args)
    if arguments_from_payload is not None:
        arguments.update(arguments_from_payload)

    # Check for optional arguments
    collection = arguments.pop("collection", "Adp")

    user = arguments.pop("user", None)
    if user is None:
        raise InvalidUsage("Unknown user: {}".format(user))

    beamline = arguments.pop("beamline", None)

    after = arguments.pop("after", None)

    method = arguments.pop("method", None)
    if method is None:
        raise InvalidUsage("Method not given")
    try:
        limit = int(arguments.pop("limit", 0))
    except ValueError:
        raise InvalidUsage("Limit needs to be a number. I got: {}".format(limit))

    # optional argument
    mergeId = arguments.pop("mergeId", None)

    import beamlines

    bl = beamlines.beamlines()

    try:
        beamline = bl[beamline]
    except KeyError:
        pass

    try:
        start_date = dateutil.parser.parse(after)
    except:
        raise InvalidUsage(
            'Data value in "after" is wrong or not given. Make sure it is in IsoFormat. I got {}:'.format(
                after
            )
        )

    match = {
        "beamline": beamline,
        "userAccount": user,
        "createdOn": {"$gte": start_date},
        "method": method,
    }
    group = {"_id": None, "count": {"$sum": 1}}

    # add optional arguments
    if mergeId is not None:
        match["mergeId"] = mergeId

    if (
        limit == 0
    ):  # used for standard datasets, pipeline with one 'match' without limit and sorting is faster
        match["seen"] = False
        query = [{"$match": match}, {"$group": group}]
    else:  # used for screening
        match2 = {"seen": False}
        query = [
            {"$match": match},
            {"$sort": {"_id": -1}},
            {"$limit": limit},
            {"$match": match2},
            {"$group": group},
        ]

    # query = [{'$match':match}, {'$sort':{'_id':-1}}, {'$limit': limit}, {'$match':match2}, {'$group':group}]

    try:
        result = mongo_ops.aggregate(collection, query)
    except mongo_ops.MongoNotConnected:
        raise InvalidUsage("Could not connect to MongoDB server", 403)

    outmsg[u"answer"] = list(result)

    if outmsg[u"answer"] == []:
        outmsg[u"answer"] = [{"_id": None, "count": 0}]

    return json.dumps(outmsg, default=json_serialhelper.json_serialhelper)
