# RasaX Chatbot Deployment

Run custom chatbot installation with Docker Compose

## Minimum Requirements

- Ubuntu server 18.04+
- 2-6 vCPUs
- 4GB RAM
- 100GB Disk space
- Python 3.6 - 3.8 (for RasaX 0.42.0)

## Setup

- Clone repo to your server and `cd`
- Run `docker-compose build` to build the `rasa-x-custom` image
- Copy `env-sample` to `.env` file and update the environment variables
- Run `docker-compose up -d` to run the app stack

## Linking to Git

RasaX connects to a second git repository to save the models and data used by the bot.

## Resources

- [Install RasaX with Docker Compose](https://rasa.com/docs/rasa-x/installation-and-setup/install/docker-compose)
- [Rasa Playground](https://rasa.com/docs/rasa/playground)
