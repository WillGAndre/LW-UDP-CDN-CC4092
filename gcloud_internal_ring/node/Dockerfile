FROM python:3

WORKDIR /app
EXPOSE 8080

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python3", "-u", "node.py"]