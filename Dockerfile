FROM python:3.8
ENV PORT 5000
ENV HOST 192.168.1.50

EXPOSE 80
COPY requirements.txt .
RUN apt-get update -y && \
    apt-get install -y python3-pip

WORKDIR ./

RUN pip install -r requirements.txt

COPY . /

ENTRYPOINT ["python", "webapp.py"]