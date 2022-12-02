import os
import openai
from principles_finder_prompt import FINDER_PROMPT
import difflib
import json

openai.api_key = os.getenv("OPENAI_API_KEY")
DEBUG = False


def get_principles_to_chapter():
    with open('principles_to_chapter.json', 'r') as f:
        out = json.load(f)
    return out


def find_relevant_chapter(principles, corpus):
    closest_principles = []
    if principles is not None:
        out = []
        for idx, principle in enumerate(principles):
            closest_principle = difflib.get_close_matches(principle, list(corpus.keys()))[0]
            closest_principles.append(closest_principle)
            out.append(''.join(corpus[closest_principle]))
        out = '\n'.join(out)
    else:
        closest_principles = None
        out = None
    return closest_principles, out


def _format_principles_finder_input(questions):
    out = FINDER_PROMPT + '\n'
    if len(questions) == 1:
        return f'{FINDER_PROMPT}\nQuestion: {questions[0]}\n\nAnswer:\n'
    else:
        for idx, question in enumerate(questions):
            if idx != len(questions)-1:
                out = out + f'Question: {question.strip()}\nResponse: ...\n'
            else:
                out = out + f'Question: {question.strip()}\n\nAnswer:\n'
        return out


def find_principles(questions, corpus):
    model_input = _format_principles_finder_input(questions)
    if DEBUG:
        print('\n' + '#'*5 + 'Principles Finder Input' + '#'*5 + '\n')
        print(model_input)
        print('#'*20)
    response = openai.Completion.create(
            model="text-davinci-003",
            prompt=model_input,
            temperature=0,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0)
    response = response['choices'][0]['text']
    if DEBUG:
        print(response)
    if 'not sure' in response.lower():
        principles = None
    else:
        principles = response.split('\n')
        principles = [i.replace('• ', '')[:-1] for i in principles]
    principles, chapter = find_relevant_chapter(principles, corpus)
    return principles, chapter


def get_completion(chat_history, principles, relevant_corpus):
    model_input = f"""Here are the two principles written by Ray Dalio in his book:


{relevant_corpus}


Complete the following conversation using the two principles from above, do not start with 'Based on the principles...':
{chat_history}"""
    if DEBUG:
        print('\n' + '#'*5 + 'Model Input' + '#'*5 + '\n')
        print(model_input)
        print('#'*20)
    response = openai.Completion.create(
            model="text-davinci-003",
            prompt=model_input,
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0)
    response = response['choices'][0]['text']
    source = '\n'.join(principles)
    response = response + f"\n\nSource:\n{source}"
    return response


class DalioBot():
    def __init__(self, corpus):
        self.corpus = corpus
        self.initial_text = "Ray Dalio: How can I help you?"
        self.chat_history = []

    def respond(self, question):
        principles, chapter = find_principles(self._format_question(question), self.corpus)
        self.chat_history.append(f'User: {question.strip()}')
        if principles is None:
            self.chat_history.pop(-1)
            response = 'Sorry, I do not know how to answer this question.'
        else:
            model_input = '\n'.join(self.chat_history) + '\nRay Dalio:'
            response = get_completion(model_input, principles, chapter)
        print(f'\nRay Dalio: {response.strip()}')
        formated_response = self._format_response(response)
        if principles is not None:
            self.chat_history.append(f'Ray Dalio: {formated_response}')
        return response

    def _format_response(self, response):
        response = response.strip().split('\n\n')[0]
        return response

    def _format_question(self, question):
        if len(self.chat_history) == 0:
            return [question]
        else:
            existing_questions = [i.split('User: ')[-1] for i in self.chat_history if 'User' in i]
            return existing_questions + [question]


if __name__ == '__main__':
    corpus = get_principles_to_chapter()
    bot = DalioBot(corpus)
    while True:
        question = input('\nUser: ')
        bot.respond(question)
