FROM python:3.11

RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN apt-get update && apt-get install -y vim nano git

ARG USER=HeidiProject
ARG REPO=mxdb-server
ARG BRANCH=dewar-logistics
ADD https://api.github.com/repos/$USER/$REPO/git/refs/heads/$BRANCH version.json
RUN git clone -b $BRANCH https://github.com/$USER/$REPO.git

RUN git config --global user.email "katemarylouisesmith@gmail.com"
RUN git config --global user.name "Kate Smith"


#COPY /mxdb-server/src/ /opt/mxdb
COPY appconfig.py /mxdb-server/src/appconfig.py

#RUN apt-get install bc
RUN pip install --upgrade pip && pip install --no-cache-dir -r /mxdb-server/requirements.txt
ENV PYTHONPATH=/mxdb-server/src/app:/mxdb-server/src/lib:/mxdb-server/src/etc:$PYTHONPATH
ENV MONGO_URI=172.23.168.188:27017/mxdb

# Default port of flask
EXPOSE 5000
WORKDIR /mxdb-server/src/
# ENTRYPOINT ["./startApp.sh"] # don't use this, it does not allow to /bin/sh to container
# CMD ["./startApp.sh","--dbloc", "linked"] # Default command to run # <--- old comman from before gunicorn
CMD ["./startApp.sh"] # Default command to run
