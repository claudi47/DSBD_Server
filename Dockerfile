FROM python:3.10.1-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apk add build-base && apk add openssl && apk add libffi-dev
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["./startup.sh"]