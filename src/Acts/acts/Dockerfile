FROM alpine:3.7

WORKDIR /acts
COPY . /acts

RUN apk add --update \
	python3 \
	python3-dev \
	&& pip3 install --no-cache-dir --upgrade pip \
	&& pip3 install Flask \
	&& pip3 install requests \
    && pip3 install flask-sqlalchemy \
    && pip3 install flask-migrate

EXPOSE 5000

CMD flask run -h 0.0.0.0
