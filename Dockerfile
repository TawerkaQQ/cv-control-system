FROM python:3.10

WORKDIR /sneaky-cv-control-system

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

#CMD ["python3", "main.py"]