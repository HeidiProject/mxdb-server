FROM python:3.11

RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN apt-get update && apt-get install -y vim nano

COPY src/ /opt/mxdb
COPY appconfig.py /opt/mxdb/appconfig.py

COPY requirements.txt .

#RUN apt-get install bc
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Default port of flask
EXPOSE 5000
WORKDIR /opt/mxdb
# ENTRYPOINT ["./startApp.sh"] # don't use this, it does not allow to /bin/sh to container
# CMD ["./startApp.sh","--dbloc", "linked"] # Default command to run # <--- old comman from before gunicorn
CMD ["./startApp.sh"] # Default command to run
