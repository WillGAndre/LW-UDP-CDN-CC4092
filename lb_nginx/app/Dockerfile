FROM python:3-alpine

EXPOSE 5000

RUN apk upgrade --no-cache && \
    apk add --virtual .build-dependencies \ 
            --no-cache \
            python3-dev \
            build-base \
            linux-headers \
            pcre-dev \
            maturin \
            curl \
            build-base \
            gcc \
            rustup \
            postgresql-client \
            bash \
            openssl \
            libgcc \
            libstdc++ \
            ncurses-libs \
            pcre

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN rustup-init -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .

RUN maturin develop
CMD ["uwsgi", "--ini", "/app/wsgi.ini"]