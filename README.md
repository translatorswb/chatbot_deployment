# RasaX Chatbot Deployment

Run custom chatbot installation with Docker Compose

## Minimum Requirements

- Ubuntu server 18.04+
- 2-6 vCPUs
- 4GB RAM
- 100GB Disk space
- Python 3.6 - 3.8 (for RasaX 0.42.0)

## Setup

- Clone repo
- The default installation path is `/etc/rasa` , however, you can install in your desired path if you set: `export RASA_HOME=~/rasa/dir`
- Run the commands below to install

```
cd chatbot_deployment
sudo chmod 777 install.sh

# -E will preserve the environment variable you set
sudo -E bash ./install.sh
```

- `cd` into your installation folder (assuming you installed to `/etc/rasa/`)
- Run `sudo docker-compose build` to build custom images
- Run `docker-compose build` to build and image from `rasa-x-custom`
- Copy `env-sample` to `.env` file and update the environment variables
- Run `sudo chown -R 1001:1001 db/` to change the permissions of the `db` postgresql local db folder
- Run `docker-compose up -d` to run the app stack
- Check running containers using `docker ps`

Once the app has started and database migrations complete, visit http://YOUR_IP_OR_DOMAIN on your browser.

To reset the default password, run `sudo python rasa_x_commands.py create --update admin me YOUR_PASSWORD`

## Linking to Git

RasaX connects to a git repository where all training data is maintained. Use this
[guide](https://rasa.com/docs/rasa-x/installation-and-setup/integrated-version-control-via-api/) to link to your repository.

## Training in Container

You can train the bot inside the RasaX container as below:

- Access container shell: `docker-compose exec rasa-x /bin/bash`
- Train bot: `rasa-train`

## Installing SSL certificate

We use Certbot as the provider for SSL certificates:

- Run `./install-ssh.sh` to install `certbot`
- Update the domain in the script `./cp-certs.sh` and run it to copy the certificates into the `certs` directory

## Resources

- [Install RasaX with Docker Compose](https://rasa.com/docs/rasa-x/installation-and-setup/install/docker-compose)
- [Rasa Playground](https://rasa.com/docs/rasa/playground)
- [Securing with SSL](https://rasa.com/docs/rasa-x/installation-and-setup/customize#securing-with-ssl)
