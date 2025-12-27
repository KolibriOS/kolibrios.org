FROM node:18-alpine as sass

RUN npm install -g sass
WORKDIR /build
COPY ./static ./static
RUN sass ./static:./static \
    --no-source-map \
    --style=compressed


FROM python:3.11-slim

WORKDIR /app

COPY . .
COPY --from=sass /build/static/ ./static/

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:80", "--workers", "4"]
