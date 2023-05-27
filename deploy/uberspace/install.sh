# run these commands on local
# scp -r deploy bscanner:
# ssh bscanner 'bash deploy/uberspace/install.sh'

cd deploy/uberspace

set -e

# create folders
mkdir -p ~/repos
git init --bare ~/repos/brandscanner.git
cp post-receive ~/repos/brandscanner.git/hooks/post-receive
chmod +x ~/repos/brandscanner.git/hooks/post-receive
mkdir -p ~/webapps/brandscanner
touch ~/ENV
ln -s /home/bscanner/ENV ~/webapps/brandscanner/.env

# https://lab.uberspace.de/guide_django.html
# install uwsgi
pip3.11 install uwsgi --user
cp uwsgi.ini ~/etc/services.d/uwsgi.ini
mkdir -p ~/uwsgi/apps-enabled
touch ~/uwsgi/err.log
touch ~/uwsgi/out.log

supervisorctl reread
supervisorctl update
supervisorctl status

# configure web server
uberspace web domain add thebrandscanner.in
uberspace web backend set thebrandscanner.in --http --port 8000

# create deamon
mkdir -p ~/uwsgi/apps-enabled/
cp django-app.ini ~/uwsgi/apps-enabled/

# configure static servers
uberspace web backend set thebrandscanner.in/static --apache
uberspace web backend set thebrandscanner.in/media --apache

# add nginx headers
uberspace web header set thebrandscanner.in/static/ expires 7d
uberspace web header set thebrandscanner.in/favicon.ico root /var/www/virtual/bscanner/html/static/favicons
uberspace web header set thebrandscanner.in/favicon.ico expires 7d

uberspace web header set thebrandscanner.in/static gzip on
uberspace web header set thebrandscanner.in/static gzip_comp_level 6
uberspace web header set thebrandscanner.in/static gzip_types "text/plain text/css text/xml application/json application/javascript application/xml+rss application/atom+xml image/svg+xml"

# instructions to setup git push
echo "Remote setup done"
echo "Run these on local"
echo "git remote add live bscanner:repos/brandscanner.git"
echo "git push live"
echo "ssh bscanner"
echo "vi ENV"
echo "python3.11 manage.py createsuperuser --settings=brandscanner.settings.production"
