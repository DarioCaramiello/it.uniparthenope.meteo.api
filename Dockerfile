FROM python:3.9

RUN apt update
RUN apt-get install -y --no-install-recommends libatlas-base-dev gfortran nginx supervisor

RUN pip3 install uwsgi

COPY ./requirements.txt /project/requirements.txt
RUN pip3 install -r /project/requirements.txt

RUN useradd --no-create-home nginx
RUN rm /etc/nginx/sites-enabled/default
RUN rm -r /root/.cache

COPY server-conf/nginx.conf /etc/nginx/
COPY server-conf/flask-site-nginx.conf /etc/nginx/conf.d/
COPY server-conf/uwsgi.ini /etc/uwsgi/
COPY server-conf/supervisord.conf /etc/supervisor/

COPY . /project/src
WORKDIR /project

# EXPOSE 50000
CMD ["/usr/bin/supervisord"]

ENV APP_SETTINGS=/project/etc/ccmmmaapi.conf
CMD flask --app /project/app run --host 0.0.0.0 --port 50000




