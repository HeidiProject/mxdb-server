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

from flask_cors import CORS, cross_origin

import mongo_operations as mongo_ops

import importlib
appconfig = importlib.import_module("{}".format("appconfig"))


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

@app.route("/api/shipment/dewars/history", methods=["POST"])
@cross_origin()
def updateDewar():
    dewar = {"DEWARHISTORYID": 1}
    return json.dumps(dewar, default=json_serialhelper.json_serialhelper)

@app.route("/api/dewars/recent",methods=["GET"])
@cross_origin()
def recentDewars():
    return {}

@app.route("/api/dewars/history",methods=["GET"])
@cross_origin()
def dewarHistory():
    return {}

@app.route("/api/beamlines/zone4",methods=["GET"])
@cross_origin()
def getDewars():
    
    results = {'TRAY-1A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-1B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-1C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-1D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-1E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-1F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-2A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-2B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-2C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-2D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-2E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-2F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-3A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-3B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-3C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-3D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-3E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-3F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-4A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-4B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-4C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-4D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-4E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-4F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-5A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-5B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-5C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-5D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-5E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-5F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-6A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-6B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-6C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-6D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-6E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-6F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-7A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-7B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-7C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-7D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-7E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-7F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-8A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-8B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-8C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-8D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-8E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-8F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-9A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-9B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-9C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-9D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-9E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-9F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-10A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-10B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-10C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-10D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-10E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-10F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-11A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-11B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-11C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-11D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-11E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-11F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-12A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-12B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-12C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-12D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-12E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-12F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-13A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-13B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-13C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-13D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-13E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-13F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-14A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-14B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-14C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-14D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-14E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-14F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-15A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-15B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-15C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-15D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-15E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-15F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-16A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-16B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-16C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-16D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-16E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-16F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-17A': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-17B': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-17C': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-17D': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-17E': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-17F': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-17G': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-17H': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-17I': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-17J': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-17K': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-17L': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-17M': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-17N': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, 'TRAY-17O': {'barcode': '', 'arrivalDate': '', 'facilityCode': '', 'status': '', 'onBeamline': False}, "TRAY-17P": {"dewarId": 71349, "barcode": "mx23694-0071349", "arrivalDate": "2024-05-15T11:01:02", "facilityCode": "DLS-MX-9999", "status": "at facility", "comments": None, "onBeamline": False, "dewarLocation": "tray-17p", "dewarContainers": ["I03-0005"], "UDC": True}}
    return json.dumps(results, default=json_serialhelper.json_serialhelper)

@app.route("/db/query", methods=["GET"])
@cross_origin()
def dbQuery():
    import dateutil.parser
    import bson

    import ast
    import dbCollections

    import beamlines

    bl = beamlines.beamlines()

    collections = dbCollections.dbCollections()
    outmsg = {}
    query = {}

    # Query can be either given as arguments or as json payload in the mesage body
    query_from_args = request.args.to_dict()
    query_from_payload = request.json

    query.update(query_from_args)
    if query_from_payload is not None:
        query.update(query_from_payload)

    try:
        query["method"] = ast.literal_eval(query["method"])
    except (ValueError, SyntaxError, KeyError):
        pass

    try:
        coll = query.pop(u"collection")
    except KeyError:
        msg = 'collection to query not specified. \
        Please use collection=value when constructing URL or include "collection" key in message. \
        Available choices: {}'.format(
            collections.collectionNames
        )
        raise InvalidUsage(msg)

    if coll not in collections.collectionNames():
        if (coll == "Users" or coll == "Tokens") and ("key" in query):
            print("inside key section")
            key = query.pop(u"key")
            if key == appconfig.dbKey:
                pass
        else:
            msg = "Collection not found in the database. Available choices: {}".format(
                collections.collectionNames
            )
            raise InvalidUsage(msg)

    # If 'before' or 'after' keys are present in query, process them to make a range query for the date
    # If 'createdOn' is explicitly given, it overwrites 'before' and 'after' values
    # If neither is given, do not query date

    dateQuery = {}
    if ("before" in query) or ("after" in query):
        try:
            before = dateutil.parser.parse(query.pop(u"before", "3000"))
            after = dateutil.parser.parse(query.pop(u"after", "1900"))
        except:
            msg = 'Can not parse date given in "before" or "after". Invalid format.'
            raise InvalidUsage(msg)
        dateQuery["createdOn"] = {"$gte": after, "$lt": before}

    if ("updated_before" in query) or ("updated_after" in query):
        try:
            before = dateutil.parser.parse(query.pop(u"updated_before", "3000"))
            after = dateutil.parser.parse(query.pop(u"updated_after", "1900"))
        except:
            msg = 'Can not parse date given in "updated_before" or "updated_after". Invalid format.'
            raise InvalidUsage(msg)
        dateQuery["lastUpdated"] = {"$gte": after, "$lt": before}

    createdOn = query.pop(u"createdOn", None)
    if createdOn != None:
        try:
            dateQuery["createdOn"] = dateutil.parser.parse(createdOn)
        except:
            msg = 'Can not parse date given in "createdOn". Invalid format.'
            raise InvalidUsage(msg)

    lastUpdated = query.pop(u"lastUpdated", None)
    if lastUpdated != None:
        try:
            dateQuery["lastUpdated"] = dateutil.parser.parse(lastUpdated)
        except:
            msg = 'Can not parse date given in "lastUpdated". Invalid format.'
            raise InvalidUsage(msg)

    # Update the query back with the parsed date range
    query.update(dateQuery)

    # Check is number of results returned from the database is limited
    nLimit = 0
    if u"limit" in query:
        nLimit = query.pop(u"limit")
        try:
            nLimit = int(nLimit)
        except ValueError:
            msg = "limit needs to be an integer number"
            raise InvalidUsage(msg)

    # Check the options if user request for sorted order
    # This is enabled only when pymongo.find() is used
    sort = False
    if u"sortkey" in query:
        sort = True
        sortKey = query.pop(u"sortkey")

    qtype = u"find"
    if u"qtype" in query:
        qtype = query.pop(u"qtype")
        queryTypes = [u"find", u"distinct", u"find_one", u"aggregate"]
        if qtype not in queryTypes:
            allqtype = "".join([u"%s, " % s for s in queryTypes])
            msg = "Invalid query type %s. Allowed qtype: %s" % (qtype, allqtype)
            raise InvalidUsage(msg)

    try:
        query[u"_id"] = bson.ObjectId(query[u"_id"])
    except (bson.errors.InvalidId, KeyError):
        pass

    # Ensure proper beamline name if given
    try:
        query["beamline"] = bl[query["beamline"]]
    except KeyError:
        pass

    if qtype == u"distinct":
        try:
            # query = query[u'key']
            key = query.pop(u"key")
        except KeyError:
            msg = "qtype=distinct requires attribute key=<query_value>"
            raise InvalidUsage(msg)

    # Parse the aggregation query:
    if qtype == u"aggregate":

        pipeline = []
        # Define supported pipeline stages, and their order
        # stages = [u'match', u'project' ,u'sort', u'group', u'sort']
        stages = [u"match", u"project", u"group", u"sort", u"limit", u"count"]
        # To support queries where two identical arguments are given
        # for instance: <url>?sort=<val>&match=<val>&sort=<val2> create stageIndex to
        # index values in werkzeug.ImmutableMultiDict
        stageIndex = {}
        for stageName in stages:
            stageIndex[stageName] = 0

        for stageName in stages:
            stageList = request.args.getlist(
                stageName
            )  # retrive data from werkzeug.ImmutableMultiDict, which returns [u"{'key':'value'}"] or [u"{'key':'value'}", u"{'key2':'value2'}"]
            if stageList != []:
                try:  # in case when the are two stage possible, but the only the 1st stage is given, i.e sort.
                    stage = stageList[stageIndex[stageName]]
                except IndexError:
                    stage = None

                if stage != None:
                    try:
                        stage = ast.literal_eval(stage)
                    except (ValueError, SyntaxError):
                        pass
                    stage = convertToIsoDate(stage)
                    stageIndex[stageName] += 1
                    stageName = (
                        "$" + stageName
                    )  # Convert to MongoDB notation for pipleine stage names
                    pipeline.append({stageName: stage})
        # print ("Pipeline", pipeline)
        query = pipeline

    ## Query the database ##
    try:
        if qtype == "distinct":
            # answer = getattr(mongo.db[coll], qtype)(key, query)
            answer = getattr(mongo_ops, qtype)(coll, key, query)
        else:
            # answer = getattr(mongo.db[coll], qtype)(query)
            answer = getattr(mongo_ops, qtype)(coll, query)
    except mongo_ops.MongoNotConnected:
        raise InvalidUsage("Could not connect to MongoDB server", 403)
    except Exception as e:
        msg = "Problem with the query: "
        raise InvalidUsage(msg + str(e))
    if (
        qtype != u"find_one"
    ):  # find_one returns only dictionary, list would return only keys
        if sort:
            answer.sort(sortKey, pymongo.DESCENDING)

        # Limit the number of returned results (NOTE: nLimit=0 returns all)
        if qtype != u"aggregate" and qtype != u"distinct":
            answer.limit(nLimit)

        outmsg[u"answer"] = list(answer)
    else:

        outmsg[u"answer"] = answer
    msgJson = json.dumps(outmsg, default=json_serialhelper.json_serialhelper)
    return msgJson


@app.route("/eigerMask", methods=["GET"])
@cross_origin()
# @crossdomain(origin='*')
def eigerMask():
    """
    Retrives Eiger mask stored in mxdb

    API:
    http://<server>:<port>/eigerMask  - retrive latest document with mask data
    http://<server>:<port>/eigerMask?fullmask=0 - retrive latest document with mask data
    http://<server>:<port>/eigerMask?fullmask=1 - retrive latest document along with full mask in numpy.ndarray
    http://<server>:<port>/eigerMask?fulldata=0 - retrive latest the document with mask data
    http://<server>:<port>/eigerMask?fulldata=1 - retrive all the document with mask data. Sets fullmask=0
    http://<server>:<port>/eigerMask?maskid=ObjID - retrive the mask with specified id from Eiger Collection. Sets fullmask=1, fulldata=0
    """
    import dbCollections
    import cPickle, bz2
    from base64 import b64encode
    import numpy as np

    collections = dbCollections.dbCollections()
    import logging

    coll = collections.Eiger
    collMask = coll + "Mask"
    outmsg = {}
    options = {}
    options = request.args.to_dict()
    keys = options.keys()
    keys = [x.lower() for x in keys]

    # lower all the keys in options
    options = dict((k.lower(), v) for k, v in options.iteritems())
    fullmask = False
    fulldata = False
    maskid = False

    if "fullmask" in options:
        try:
            v = int(options["fullmask"])
        except ValueError:
            msg = "eigerMask: fullmask options can have values 0 and 1."
            raise InvalidUsage(msg)

        if v > 0:
            fullmask = True
            logging.info("eigerMask: retrival of fullmask requested")

    if "fulldata" in options:
        try:
            v = int(options["fulldata"])
        except ValueError:
            msg = "eigerMask: fulldata options can have values 0 and 1."
            raise InvalidUsage(msg)

        if v > 0:
            fulldata = True
            fullmask = False
            logging.info("eigerMask: retrival of fulldata requested. Fullmask set to 0")

    if "maskid" in options:
        v = options["maskid"]
        fulldata = False
        fullmask = True
        try:
            maskid = bson.ObjectId(v)
        except bson.errors.InvalidId:
            msg = "Invalid ObjectID of the document with mask"
            raise InvalidUsage(msg)

    if maskid:  # Retrive mask with specified ID
        try:
            doc = mongo.db[coll].find_one(
                {"_id": maskid}
            )  # find mask info in collection Eiger
        except Exception as e:
            msg = "eigerMask: Cannot retrive mask data."
            raise InvalidUsage(msg)

    else:  # Retrive latest mask or other queries
        try:
            answer = list(mongo.db[coll].find().sort("_id", pymongo.DESCENDING))
            if fulldata:
                doc = answer
            else:
                doc = answer[0]
        except Exception as e:
            msg = "eigerMask: Cannot retrive mask data."
            raise InvalidUsage(msg)

    # if full mask is requested
    if fullmask:
        maskID = bson.ObjectId(doc["value"]["data"])
        try:
            answerMask = mongo.db[collMask].find_one({"_id": maskID})
            mask = answerMask["data"]
        except Exception as e:
            msg = "eigerMask: Cannot retrive binary mask."
            raise InvalidUsage(msg)

        # Unpack mask from pickle and bz2, encode with base64 and send
        mask = cPickle.loads(mask)
        mask = bz2.decompress(mask)

        mask = np.fromstring(mask, dtype=doc["value"]["type"]).reshape(
            doc["value"]["shape"]
        )
        mask = b64encode(mask)

        doc["value"]["data"] = mask

    outmsg[u"answer"] = doc

    msgJson = json.dumps(outmsg, default=json_serialhelper.json_serialhelper)

    return msgJson
