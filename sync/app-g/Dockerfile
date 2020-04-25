FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000

CMD export FLASK_APP=app.py && export FLASK_DEBUG=1 && flask run -p 5000 -h 0.0.0.0