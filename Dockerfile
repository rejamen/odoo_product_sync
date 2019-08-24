# Pull base image
FROM odoo:12.0

# Install dependencies
COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt
