# RasaX Chatbot Deployment

Run custom chatbot installation with Docker Compose

## Minimum Requirements

- Ubuntu server 18.04+
- 2-6 vCPUs
- 4GB RAM
- 100GB Disk space
- Python 3.6 - 3.8 (for RasaX 0.42.0)

## Setup

- Clone repo to your server and `cd` into it
- Run `docker-compose build` to build and image from `rasa-x-custom`
- Copy `env-sample` to `.env` file and update the environment variables
- Run `sudo chown -R 1001:1001 db/` to change the permissions of the `db` postgresql local db folder
- Run `docker-compose up -d` to run the app stack

Once the app has started and database migrations complete, visit http://YOUR_IP_OR_DOMAIN on your browser.

To reset the default password, run `sudo python rasa_x_commands.py create --update admin me YOUR_PASSWORD`

## Linking to Git

RasaX connects to a second git repository to save the models and data used by the bot.

## Resources

- [Install RasaX with Docker Compose](https://rasa.com/docs/rasa-x/installation-and-setup/install/docker-compose)
- [Rasa Playground](https://rasa.com/docs/rasa/playground)
