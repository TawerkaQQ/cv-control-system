FROM python:3.10

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

WORKDIR /sneaky-cv-control-system/