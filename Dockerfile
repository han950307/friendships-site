FROM python

ADD . /friendships-site
WORKDIR /friendships-site
RUN apt update -y
RUN apt install -y apt-transport-https apt-utils
RUN apt install -y build-essential libexpat1-dev libpcre3-dev apache2-dev apache2 libssl-dev postgresql
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt
# RUN python manage.py makemigrations
# RUN python manage.py migrate --noinput
RUN python manage.py test
RUN sed -i "s|DEBUG = True|DEBUG = False |g" ./friendsite/production_secrets.py
RUN sed -i "s|LOCAL = True|LOCAL = False |g" ./friendsite/production_secrets.py
# RUN python manage.py migrate --noinput
RUN python manage.py collectstatic --noinput
RUN groupadd -r django && useradd --no-log-init -r -g django django
CMD mod_wsgi-express start-server --port=80 --url-alias /static /static/ --application-type module --user django --group django friendsite.wsgi
