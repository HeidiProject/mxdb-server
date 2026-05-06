FROM python:3.11-slim

# Set bash as the default shell
RUN rm /bin/sh && ln -s /bin/bash /bin/sh


# Configure internal PyPI mirror for DMZ

COPY pip.conf /etc/pip.conf



# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Default port of Flask
EXPOSE 5000

# Create the working directory
RUN mkdir -p /opt/mxdb
COPY src/ /opt/mxdb
WORKDIR /opt/mxdb

# Command to run the application
CMD ["/opt/mxdb/startApp.sh"]

