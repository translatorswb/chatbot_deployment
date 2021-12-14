sudo cp /etc/letsencrypt/live/example.com/privkey.pem /etc/rasa/certs/
sudo cp /etc/letsencrypt/live/example.com/fullchain.pem /etc/rasa/certs/
sudo certbot renew
sudo chmod 777 /etc/rasa/certs/fullchain.pem
sudo chmod 777 /etc/rasa/certs/privkey.pem
