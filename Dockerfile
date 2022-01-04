FROM python:3.10.1-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DB_PASSWORD=ciaoatutti
ENV DB_USERNAME=claudi47
ENV DB_URL=mongo
ENV DB_PORT=27017

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apk add build-base && apk add openssl && apk add libffi-dev
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./manage.py", "runserver", "8000" ]