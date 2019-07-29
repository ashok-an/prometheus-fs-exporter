FROM python:3.6-alpine

ADD main.py /
ADD config.json.sample /
ADD config.json /
ADD requirements.txt /

RUN pip install -r requirements.txt

ENV HTTP_PORT 19090
EXPOSE ${HTTP_PORT}

ENTRYPOINT ["python", "main.py"]
CMD []
