#!/usr/bin/env python
from flask import Flask

# from flask.ext.pymongo import PyMongo
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin

import importlib
import os

import timeouts_conf

appconfig = importlib.import_module("{}".format("appconfig"))

MONGO_CONNECT_TIMEOUT = timeouts_conf.MONGO_CONNECT_TIMEOUT
NGINX_UPSTREAM_SERVER_TIMEOUT = timeouts_conf.NGINX_UPSTREAM_SERVER_TIMEOUT

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = appconfig.dbURI
mongo = PyMongo(app)

from app import insertsView
from app import queryView
from app import mergeStatusView
from app import streamView
from app import userUtilsView
from app import updateView
from app import updateADPView
from app import updateShippingView
from app import trackerQueryView
