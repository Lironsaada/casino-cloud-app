FROM python:3.11-slim

WORKDIR /app

COPY app ./app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Create /data and add default users.json
RUN mkdir /data && echo "{}" > /data/users.json

ENV FLASK_ENV=production

CMD ["python", "app/app.py"]

