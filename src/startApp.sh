#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/opt/mxdb/app:/opt/mxdb/etc:/opt/mxdb/lib

gunicorn app:app --worker-class gevent --workers 1 --certfile /etc/certificates/certs.pem --keyfile /etc/certificates/certs.key --bind 0.0.0.0:5000  --log-file=- --access-logfile=-