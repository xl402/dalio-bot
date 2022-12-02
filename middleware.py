from prototype import DalioBot
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_cors import CORS
import requests

app = Flask(__name__)
api = Api(app)
CORS(app)


class status (Resource):
    def get(self):
        try:
            return {'data': 'Api is Running'}
        except:
            return {'data': 'An Error Occurred during fetching Api'}


class StateLessBot(Resource):
    def __init__(self):
        self.bot = DalioBot()

    def post(self):
        json_data = request.get_json(force=True)
        text = json_data['input']
        model_input, chat_history = self.split_input_and_history(text)
        self.bot.chat_history = self._format_history(chat_history)
        print(chat_history)
        print(model_input)
        response = self.bot.respond(model_input)
        self.bot.chat_history = []
        return jsonify(data=response)

    def split_input_and_history(self, text):
        text = text.split('\n')
        last_two = text[-2:]
        model_input = last_two[0].split('User: ')[-1]
        chat_history = text[:-2]
        return model_input, chat_history

    def _format_history(self, text):
        out = []
        for chat in text:
            out.append(chat.replace('(I am not confident) - ', ''))
        return out


api.add_resource(status, '/')
api.add_resource(StateLessBot, '/chat')

if __name__ == '__main__':
    app.run()
