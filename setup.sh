python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

sudo yum install nginx
sudo mv conf/backend /etc/nginx/sites-available
sudo systemctl start nginx

cd backend
python3 manage.py migrate

sudo python3 -m venv /opt/certbot/
sudo /opt/certbot/bin/pip install --upgrade pip
sudo /opt/certbot/bin/pip install certbot certbot-nginx
sudo ln -s /opt/certbot/bin/certbot /usr/bin/certbot
sudo certbot --nginx

