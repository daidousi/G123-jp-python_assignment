FROM python:3.10

LABEL MAINTAINER="Mark Cheng"
LABEL GitHub="https://github.com/daidousi/G123-jp-python_assignment"
LABEL version="1.0"
LABEL description="A Docker container to serve G123-jp-python_assignment"

RUN pip install --upgrade pip

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY decryptAPIKEY.py /app
COPY schema.sql /app
COPY get_raw_data.py /app
RUN mkdir -p /app/key
COPY key /app/key
COPY financial /app

CMD ["/bin/bash", "-c", "python3 get_raw_data.py; python3 run.py"]
