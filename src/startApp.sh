#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/opt/mxdb/app:/opt/mxdb/etc:/opt/mxdb/lib

# number of Gunicorn workes 2*NPROC + 1
NPROC=1
NWORKERS=`echo "$NPROC*2 + 1" | bc `

gunicorn app:app --worker-class gevent --workers $NWORKERS --certfile /etc/certificates/certs.pem --keyfile /etc/certificates/certs.key --bind 0.0.0.0:5000  --log-file=- --access-logfile=-