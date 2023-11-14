FROM python:3.11-slim

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

COPY src/ /opt/mxdb
COPY requirements.txt .

#RUN apt-get install bc
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Default port of flask
EXPOSE 5000
WORKDIR /opt/mxdb
# ENTRYPOINT ["./startApp.sh"] # don't use this, it does not allow to /bin/sh to container
# CMD ["./startApp.sh","--dbloc", "linked"] # Default command to run # <--- old comman from before gunicorn
CMD ["./startApp.sh"] # Default command to run
