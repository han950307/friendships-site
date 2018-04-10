set -e

eval "add-apt-repository ppa:jonathonf/python-3.6"
eval "apt update"

eval "apt install build-essential libexpat1-dev libpcre3-dev python3.6 python3.6-dev postgresql postgresql-contrib linuxbrew-wrapper python3-pip apache2-dev python-dev python-pip apache2 libssl-dev"
echo "alias python='python3.6'" >> ~/.bashrc
echo "alias pip='python3.6 -m pip'" >> ~/.bashrc
echo "alias sudo='sudo '" >> ~/.bashrc
echo "alias sp='python manage.py shell_plus --ipython'" >> ~/.bashrc
eval "source ~/.bashrc"
eval "brew install libtiff libjpeg webp little-cms2"
eval "mkdir tmp"
eval "cd tmp"
eval "wget http://mirror.cc.columbia.edu/pub/software/apache//apr/apr-1.6.3.tar.gz"
eval "wget http://mirror.cc.columbia.edu/pub/software/apache//apr/apr-util-1.6.1.tar.gz"
eval "wget http://mirror.cc.columbia.edu/pub/software/apache//apr/apr-iconv-1.2.2.tar.gz"
eval "wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.6.3.tar.gz"
eval "tar xzf apr-1.6.3.tar.gz"
eval "tar xzf apr-util-1.6.1.tar.gz"
eval "tar xzf apr-iconv-1.2.2.tar.gz"
eval "tar xzf 4.6.3.tar.gz"
eval "cd apr-1.6.3"
eval "./configure"
eval "make"
eval "make install"
eval "cd ../apr-util-1.6.1"
eval "./configure --with-apr=/usr/local/apr"
eval "make"
eval "make install"
eval "cd ../apr-iconv-1.2.2"
eval "./configure --with-apr=/usr/local/apr"
eval "make"
eval "make install"
eval "cd ../mod_wsgi-4.6.3"
eval "--with-python=/usr/bin/python3.6"
eval "make"
eval "make install"
echo "LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so" >> /etc/apache2/mods-available/wsgi.load
eval "a2enmod wsgi"
eval "a2enmod ssl"
eval "a2ensite default-ssl"
eval "service apache2 reload"
eval "python3.6 -m pip install --upgrade pip"
eval "python3.6 -m pip install psycopg2-binary Django Pillow django-extensions ipython virtualenv django-reversion requests django-crontab pytz djangorestframework markdown django-filter pydkim omise django-formtools"

eval "cd ~/tmp"
eval "git clone https://github.com/datasift/gitflow"
eval "cd gitflow"
eval "git checkout develop"
eval "sudo ./install.sh"
eval "git hf init"
eval "sudo git hf upgrade"

eval "git clone https://github.com/AGWA/git-crypt.git"
eval "cd git-crypt"
eval "make"
eval "sudo cp git-crypt /usr/local/bin/"

eval "rm -rf ~/tmp"

sed -i '13iAlias /static/ /home/ubuntu/static/\n' /etc/apache2/sites-enabled/000-default.conf
sed -i '14iAlias /media/ /home/ubuntu/media/' /etc/apache2/sites-enabled/000-default.conf
sed -i '15i' /etc/apache2/sites-enabled/000-default.conf
sed -i '16i<Directory /home/ubuntu/static>' /etc/apache2/sites-enabled/000-default.conf
sed -i '17iRequire all granted' /etc/apache2/sites-enabled/000-default.conf
sed -i '18i</Directory>' /etc/apache2/sites-enabled/000-default.conf
sed -i '19i<Directory /home/ubuntu/media>' /etc/apache2/sites-enabled/000-default.conf
sed -i '20iRequire all granted' /etc/apache2/sites-enabled/000-default.conf
sed -i '21i</Directory>' /etc/apache2/sites-enabled/000-default.conf
sed -i '22i' /etc/apache2/sites-enabled/000-default.conf
sed -i '23i<Directory /home/ubuntu/friendships-site/friendsite>' /etc/apache2/sites-enabled/000-default.conf
sed -i '24i<Files wsgi.py>' /etc/apache2/sites-enabled/000-default.conf
sed -i '25iRequire all granted' /etc/apache2/sites-enabled/000-default.conf
sed -i '26i</Files>' /etc/apache2/sites-enabled/000-default.conf
sed -i '27i</Directory>' /etc/apache2/sites-enabled/000-default.conf
sed -i '28i' /etc/apache2/sites-enabled/000-default.conf
sed -i '30i#DocumentRoot /home/ubuntu/example' /etc/apache2/sites-enabled/000-default.conf
sed -i '31iWSGIDaemonProcess friendships python-path=/home/ubuntu/friendships-site' /etc/apache2/sites-enabled/000-default.conf
sed -i '32iWSGIProcessGroup friendships' /etc/apache2/sites-enabled/000-default.conf
sed -i '33iWSGIScriptAlias / /home/ubuntu/friendships-site/friendsite/wsgi.py' /etc/apache2/sites-enabled/000-default.conf
sed -i '34iWSGIPassAuthorization On' /etc/apache2/sites-enabled/000-default.conf

sed -i '6iAlias /static/ /home/ubuntu/static/\n' /etc/apache2/sites-enabled/000-default.conf
sed -i '7iAlias /media/ /home/ubuntu/media/' /etc/apache2/sites-enabled/000-default.conf
sed -i '8i' /etc/apache2/sites-enabled/000-default.conf
sed -i '9i<Directory /home/ubuntu/static>' /etc/apache2/sites-enabled/000-default.conf
sed -i '10iRequire all granted' /etc/apache2/sites-enabled/000-default.conf
sed -i '11i</Directory>' /etc/apache2/sites-enabled/000-default.conf
sed -i '12i<Directory /home/ubuntu/media>' /etc/apache2/sites-enabled/000-default.conf
sed -i '13iRequire all granted' /etc/apache2/sites-enabled/000-default.conf
sed -i '14i</Directory>' /etc/apache2/sites-enabled/000-default.conf
sed -i '15i' /etc/apache2/sites-enabled/000-default.conf
sed -i '16i<Directory /home/ubuntu/friendships-site/friendsite>' /etc/apache2/sites-enabled/000-default.conf
sed -i '17i<Files wsgi.py>' /etc/apache2/sites-enabled/000-default.conf
sed -i '18iRequire all granted' /etc/apache2/sites-enabled/000-default.conf
sed -i '19i</Files>' /etc/apache2/sites-enabled/000-default.conf
sed -i '20i</Directory>' /etc/apache2/sites-enabled/000-default.conf
sed -i '21i' /etc/apache2/sites-enabled/000-default.conf
sed -i '22i#DocumentRoot /home/ubuntu/example' /etc/apache2/sites-enabled/000-default.conf
sed -i '23iWSGIDaemonProcess friendship python-path=/home/ubuntu/friendships-site' /etc/apache2/sites-enabled/000-default.conf
sed -i '24iWSGIProcessGroup friendship' /etc/apache2/sites-enabled/000-default.conf
sed -i '25iWSGIScriptAlias / /home/ubuntu/friendships-site/friendsite/wsgi.py' /etc/apache2/sites-enabled/000-default.conf
sed -i '26iWSGIPassAuthorization On' /etc/apache2/sites-enabled/000-default.conf

eval "service apache2 restart"

eval "cd ~/friendships-site/"
eval "git-crypt unlock ~/friendshipskey.pem"
