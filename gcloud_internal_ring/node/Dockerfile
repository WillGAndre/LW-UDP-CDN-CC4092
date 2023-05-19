FROM python:3

WORKDIR /app

RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python3", "-u", "node.py"]