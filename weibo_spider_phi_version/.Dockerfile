FROM python:3.7
ADD . /code
WORKDIR /code
RUN pip install -r requirement.txt