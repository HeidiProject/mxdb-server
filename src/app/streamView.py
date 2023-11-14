from app import app, mongo
from flask import render_template

from flask import request, jsonify
from flask import Response
from flask_pymongo import pymongo
import json, bson
from bson import json_util

import datetime

from error_handler import InvalidUsage
import json_serialhelper

import gevent
import numpy as np

from datetime import timedelta, datetime
from flask import make_response, request, current_app
from functools import update_wrapper

import mongo_operations as mongo_ops
import pymongo
import logging

from flask_cors import CORS, cross_origin


def connect_to_db(user, beamline, timestamp):
    # Seems tailable cursor does not throw ant exceptions on connection until cursor.next() is executed
    return mongo.db.Stream.find(
        {"userAccount": user, "beamline": beamline, "lastUpdated": {"$gte": timestamp}},
        cursor_type=pymongo.CursorType.TAILABLE_AWAIT,
    )


# Stream interface
def event(user, beamline, now):

    with app.app_context():

        cursor = connect_to_db(user, beamline, now)

        while True:
            try:
                doc = cursor.next()
                try:
                    event_name = doc["method"]
                except KeyError:
                    event_name = "other"

                event = "event: {}\n".format(event_name)
                yield event + "data: " + json.dumps(
                    doc, default=json_serialhelper.json_serialhelper
                ) + "\n\n"
                # Test code do dispatch unnamed SSE
                # yield 'data: ' + json.dumps(doc,default=json_serialhelper.json_serialhelper) + '\n\n'
                gevent.sleep(0.1)
            except StopIteration:
                gevent.sleep(1.0)
            except pymongo.errors.AutoReconnect:
                gevent.sleep(5.0)
                now = datetime.now()
                logging.warning(
                    "STREAM: connection to mxdb broken. Trying to re-connect"
                )
                cursor = connect_to_db(user, beamline, now)


@app.route("/stream/<beamline>/<user>", methods=["GET"])
@cross_origin()
def stream(user, beamline):
    import beamlines

    bl = beamlines.beamlines()

    # Ensure proper beamline name
    try:
        beamlineLabel = bl[beamline]
    except KeyError:
        raise InvalidUsage(
            "Invalid beamline name. Allowed values %s" % str(bl.beamlineNames()), 404
        )

    now = datetime.now()
    resp = Response(event(user, beamlineLabel, now))
    resp.headers["Content-Type"] = "text/event-stream"
    resp.headers["Cache-Control"] = "no-cache"

    return resp


# For SSE and Nginx see:
# https://serverfault.com/questions/801628/for-server-sent-events-sse-what-nginx-proxy-configuration-is-appropriate/801629
# https://stackoverflow.com/questions/21630509/server-sent-events-connection-timeout-on-node-js-via-nginx
