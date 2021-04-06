import os
import logging
from slack import WebClient
from slack.errors import SlackApiError

# logging setup
logging.basicConfig(filename='/tmp/webscraper_slack_messenger.log',
                    filemode='w', level=logging.INFO, format='%(asctime)s - '
                                                             '%(levelname)s:'
                                                             ' %(message)s)')


class SlackMessenger:
    def __init__(self):
        self.client = WebClient(os.environ['SLACK_GPU_SNIFFER_TOKEN'])

    def send_message(self, msg: str, receiving_channel: str = '#general'):
        try:
            response = self.client.chat_postMessage(
                channel=receiving_channel,
                text=msg)
            assert response["message"]["text"] == msg
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth',
            # 'channel_not_found'
            logging.error(f"Got an error: {e.response['error']}")
