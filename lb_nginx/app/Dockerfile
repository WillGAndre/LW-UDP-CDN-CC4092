FROM python:3-alpine

EXPOSE 5000

RUN apk add --virtual .build-dependencies \ 
            --no-cache \
            python3-dev \
            build-base \
            linux-headers \
            pcre-dev

RUN apk add --no-cache pcre

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .

RUN apk del .build-dependencies && rm -rf /var/cache/apk/*

CMD ["uwsgi", "--ini", "/app/wsgi.ini"]
