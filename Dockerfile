FROM python:3.6-alpine

ADD main.py /
ADD config.json.sample /
ADD config.json /
ADD requirements.txt /

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]
CMD []
