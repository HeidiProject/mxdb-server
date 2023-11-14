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

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/db/update", methods=["POST"])
def dbUpdate():
    """
        Usage: <server>/db/insert?collection=<Datasets|MergeState....>
        where collection specifies collection in MongoDB

        Alternative usage: <server>/db/insert
        where {colleciton:<Datasets|MergeState....>}

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

    # Check for optional arguments
    parse_metadata = options.pop("parse_metadata", False)
    upsert = bool(options.pop("upsert", False))
    query_parser = options.pop("query_parser", "default")
    update_parser = options.pop("update_parser", "default")

    if query_parser in dir({}):  # prevent user from running any other dict method
        raise InvalidUsage("Cannot execute query parser: {}".format(query_parser))

    if update_parser in dir({}):  # prevent user from running any other dict method
        raise InvalidUsage("Cannot execute update parser: {}".format(update_parser))

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

    query = message.pop("query", None)
    if query is None:
        err_msg = '"query" key not specified in the message. It should containd information to look up which document to update:\
        {"query":{"_id":"someID"}} or {"query":{"userAccount":"e10003", "beamline":"X06SA"}'
        raise InvalidUsage(err_msg)

    parsedQuery = messageParser.messageParser(query)

    try:
        parsed_query = getattr(parsedQuery, query_parser)()  # True/False
    except AttributeError:
        raise InvalidUsage(
            "Wrong parser method for query_parser specified. I got {}".format(
                query_parser
            )
        )

    if not parsed_query:
        valid_keys = getattr(parsedQuery, "{}_keys".format(query_parser))
        raise InvalidUsage(
            "Cannot parse query dictionary. Did not find all the required keys: {}".format(
                valid_keys
            )
        )

    update = message.pop("update", None)
    if update is None:
        err_msg = '"update" key not specified in the message. It should containd information to update:\
        {"update":{"userAccount":"e10033"}} or {"update":{"statusHistory.completed":someISOTime}}'
        raise InvalidUsage(err_msg)

    parsedUpdate = messageParser.messageParser(update)
    try:
        parsed_update = getattr(parsedUpdate, update_parser)()  # True/False
    except AttributeError:
        raise InvalidUsage(
            "Wrong parser method for update_parser specified. I got {}".format(
                update_parser
            )
        )

    if not parsed_update:
        valid_keys = getattr(parsedUpdate, "{}_keys".format(update_parser))
        raise InvalidUsage(
            "Cannot parse update dictionary. Did not find all the required keys: {}".format(
                valid_keys
            )
        )

    if parse_metadata:
        parsedUpdate.gen_metadata()

    update_many = options.pop("update_many", False)
    if update_many:
        try:
           # result = mongo.db[collection].update_many(parsedQuery,{'$set':parsedUpdate}, upsert=upsert)
            result = mongo_ops.update_many(collection, parsedQuery, parsedUpdate, upsert=upsert)
        except mongo_ops.MongoNotConnected:
            raise InvalidUsage("Could not connect to MongoDB server", 403)
    else:
        try:
            # result = mongo.db[collection].update_one(parsedQuery,{'$set':parsedUpdate}, upsert=upsert)
            result = mongo_ops.update_one(
                collection, parsedQuery, parsedUpdate, upsert=upsert
            )
        except mongo_ops.MongoNotConnected:
            raise InvalidUsage("Could not connect to MongoDB server", 403)

    outmsg["status"] = "OK"
    outmsg["matched_count"] = result.matched_count
    outmsg["modified_count"] = result.modified_count
    outmsg["upserted_id"] = result.upserted_id

    if result.matched_count == 0 and not upsert:
        err_msg = "Did not match any documents to update."
        raise InvalidUsage(err_msg)

    return json.dumps(outmsg, default=json_serialhelper.json_serialhelper)
