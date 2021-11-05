FROM python:3.10
ADD . /Analyser
WORKDIR /Analyser
RUN pip install --upgrade pip
RUN pip install -r requirements.txt