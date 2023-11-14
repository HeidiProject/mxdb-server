from app import app, mongo
from flask import render_template

from flask import request, jsonify
from flask import Response
from flask_pymongo import pymongo
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
import socket

import mongo_operations as mongo_ops


@app.route("/<beamline>/eaccount2uuid/<user>", methods=["GET"])
# @crossdomain(origin='*')
def eaccount2uuid(beamline, user):
    import beamlines

    bl = beamlines.beamlines()

    # Ensure proper beamline name
    try:
        beamlineLabel = bl[beamline]
    except KeyError:
        raise InvalidUsage(
            "Invalid beamline name. Allowed values %s" % str(bl.beamlineNames()), 404
        )

    # answer = mongo.db.Users.find_one({'_id':user})
    try:
        answer = mongo_ops.find_one(collection="Users", query={"_id": user})
    except mongo_ops.MongoNotConnected:
        raise InvalidUsage("Could not connect to MongoDB server", 403)

    if answer is None:
        raise InvalidUsage("user %s not found" % user, 404)
    hostname = socket.gethostname()

    link = "http://%s/%s/%s" % (hostname, beamlineLabel, answer["uuid"])
    answer["link"] = link
    answer["beamline"] = beamlineLabel
    msgJson = json.dumps(answer, default=json_serialhelper.json_serialhelper)
    return msgJson


@app.route("/<beamline>/uuid2eaccount/<uu>", methods=["GET"])
# @crossdomain(origin='*')
def uuid2eaccount(beamline, uu):
    import beamlines

    bl = beamlines.beamlines()

    # Ensure proper beamline name
    try:
        beamlineLabel = bl[beamline]
    except KeyError:
        raise InvalidUsage(
            "Invalid beamline name. Allowed values %s" % str(bl.beamlineNames()), 404
        )
    # answer = mongo.db.Users.find_one({'uuid':uu})
    try:
        answer = mongo_ops.find_one(collection="Users", query={"uuid": uu})
    except mongo_ops.MongoNotConnected:
        raise InvalidUsage("Could not connect to MongoDB server", 403)

    if answer is None:
        raise InvalidUsage("uuid %s not found" % uu, 404)

    answer["beamline"] = beamlineLabel
    msgJson = json.dumps(answer, default=json_serialhelper.json_serialhelper)
    return msgJson
