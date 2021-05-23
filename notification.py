import os
import yaml
from pushover import Client

tokens = yaml.safe_load(open('tokens.yml'))


def init_client():
    client = Client(tokens['pushover_user_key'], api_token=tokens['pushover_token'])
    return client


def send_message(message: str, title: str, attachment_path: str):
    pushover_client = init_client()
    if attachment_path:
        with open(os.path.expanduser(attachment_path), 'rb') as image:
            pushover_client.send_message(message, title=title,
                                         attachment=image)
    else:
        pushover_client.send_message(message, title=title)
