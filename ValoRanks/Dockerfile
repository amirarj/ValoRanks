FROM python:3.7-slim-stretch
COPY main.py .

RUN pip install tweepy --upgrade
RUN pip install redis --upgrade


ENTRYPOINT [ "python3" ]
CMD ["main.py"]
