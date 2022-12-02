from chai_py import ChaiBot, Update
import requests


DALIO_URL = 'http://63ef-185-205-174-218.ngrok.io/chat'
FIREBASEURL = "https://dalio-demo-conversations-default-rtdb.firebaseio.com/conversations.json"


class Bot(ChaiBot):
    def setup(self):
        self.logger.info("Setting up...")
        self.conversation = []

    def reset_history_if_too_long(self):
        if len('\n'.join(self.conversation)) >= 10000:
            self.conversation = [self.conversation[-1]]

    async def on_message(self, update: Update) -> str:
        latest_msg = update.latest_message.text
        if latest_msg == '__first':
            response = 'Hi, I am Ray Dalio, founder of Bridge Water, author of Principles. How may I help you?'
        elif f'User: {latest_msg}' == self._get_last_user_message():
            # this is retry mode
            # pop last ray's response
            old_resp = self.conversation.pop(-1)
            self.reset_history_if_too_long()
            model_input = '\n'.join(self.conversation)
            # self._post_retried_response_to_firebase(model_input, old_resp)
            result = requests.post(DALIO_URL, json={'input': model_input})
            response = result.json()['data']
            formatted_response = self._format_response(response)
            self.conversation.append(f'Ray Dalio: {formatted_response}')
        else:
            self.conversation.append(f'User: {latest_msg}')
            self.reset_history_if_too_long()
            model_input = '\n'.join(self.conversation) + '\nRay Dalio:'
            result = requests.post(DALIO_URL, json={'input': model_input})
            response = result.json()['data']
            formatted_response = self._format_response(response)
            self.conversation.append(f'Ray Dalio: {formatted_response}')
        return response.strip()

    def _format_response(self, response):
        response = response.strip().split('\n\n')[0]
        return response.strip()

    def _get_last_user_message(self):
        if len(self.conversation) <= 1:
            return None
        else:
            return self.conversation[-2]

    def _post_retried_response_to_firebase(self, model_input, old_resp):
        requests.post(FIREBASEURL, json={'input': model_input,
                                         'response': old_resp.split('Ray:')[-1],
                                         'score': -1})
