import json
from time import time
from openai import OpenAI
from dotenv import load_dotenv
import os
import asyncio
from pypdf import PdfReader

import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
nltk.download('punkt')


# https://github.com/matthewreagan/WebstersEnglishDictionary/blob/master/dictionary.json
#english_dict = json.loads(open('../dictionary.json').read())
from . import worddictionary

def is_citation(match, english_dict=worddictionary.ENGLISH_DICT):
     words = match.split()
     word_total = sum(1 if english_dict.get(word.lower()) else 0 for word in words)
     if words and len(words) > 1 and word_total / len(words) >= 0.5:
          #print(f"Not citation: {words}")
          return False
     #print(f"Citation: {words}")
     return True

def remove_references(text):
    bracket_dict = {"(": ")", "[": "]"}
    bracket = None
    text_inside_brackets = []
    for letter in text:
        if letter in bracket_dict:
            bracket = letter
            inside_bracket = ""
        elif bracket and letter in bracket_dict[bracket]:
            text_inside_brackets.append(inside_bracket)
            bracket = None
        elif bracket:
            inside_bracket += letter

    replacements = []
    removed_citations = []
    for word in text_inside_brackets:
        if is_citation(word):
            removed_citations.append(word)
            replacements.append("")
        else:
            replacements.append(word)

    for i in range(len(text_inside_brackets)):
        text = text.replace(text_inside_brackets[i], replacements[i])

    text = text.replace("()", "")
    text = text.replace("[]", "")
    return text

load_dotenv()
apikey = os.environ['OPENAI_KEY']

def ai_remove_footnotesNcites(input):

     client = OpenAI(
     # This is the default and can be omitted
     api_key = apikey,
     )

     chat_completion = client.chat.completions.create(
     messages=[
          {
               "role": "system",
               "content": f"you are a machine that takes in academic articles and returns them without footnotes and citaions. DO NOT SUMMAIRIZE IT OR CHANGE ANY TEXT! do not waste time describing what you have done! be careful when dealing with things like names with abbreiations.process this text: {input}",
          }
     ],
     model= "gpt-4o-mini-2024-07-18", #"gpt-3.5-turbo",
     )

     return chat_completion.choices[0].message.content

def ai_rem_footcite(input):
     client = OpenAI(
     # This is the default and can be omitted
     api_key = apikey,
     )

     chat_completion = client.chat.completions.create(
     messages=[
          #{
          #     "role": "system",
          #     "content": f"you are a machine that takes in academic articles and returns them without footnotes and citaions. you do not waste time describing what you have done. process this text: {input}",
          #}
          #{
          #     "role": "system",
          #     "content": f"you are a machine that takes in academic articles and returns them without footnotes and citaions. If the entire text is footnotes then return '...'. DO NOT SUMMAIRIZE IT OR CHANGE ANY TEXT! do not waste time describing what you have done! be careful when dealing with things like names with abbreiations.process this text: {input}",
          #}
          {
               "role": "system",
               "content": f"you are a machine that takes in academic articles and returns them without footnotes and citaions.DO NOT SUMMAIRIZE IT OR CHANGE ANY TEXT! do not waste time describing what you have done! be careful when dealing with things like names with abbreiations. Add a gap for paragraphs if you think there should be one.",
          },
          {
               "role": "system",
               "content": f"remove the footnotes and citations from the following text: {input}",
          }

     ],
     model="gpt-4o-mini-2024-07-18", #model="gpt-3.5-turbo-0125",
     )

     return chat_completion.choices[0].message.content

def long_ai_rem_footcite(text):
     sentences = sent_tokenize(text)
     divides = (len(text) // 5500) + 1
     # if doesn't divide equally it needs to be assigned
     remains = len(sentences) % divides
     block_size = len(sentences) // divides
     prev_index = 0
     curr_index = block_size
     text_arr = []

     if remains > 0:
          # Calculate the base value for each number
          base_value = remains // divides
          # Calculate the remainder
          remainder = remains % divides
          # Initialize the result array
          arr_remain = [base_value] * divides
          # Distribute the remainder evenly
          for i in range(remainder):
               arr_remain[i] += 1
     count = 0
     while curr_index <= len(sentences):
          curr_index += arr_remain[count]
          block = sentences[prev_index:curr_index]
          joined_text = '. '.join(block)
          text_arr.append(joined_text)
          prev_index = curr_index
          curr_index += block_size
          count+=1
     count = 1
     fin_arr = []
     #print(text_arr[1])
     for textblock in text_arr:
          retblock = ai_rem_footcite(textblock)
          fin_arr.append(retblock)
     return_text = ' '.join(fin_arr)
     return return_text


#def ai_rem_footcite(input):
#     client = OpenAI(
#     # This is the default and can be omitted
#     api_key = apikey,
#     )
#
#     chat_completion = client.chat.completions.create(
#     messages=[
#          {
#               "role": "system",
#               "content": f"you are a machine that takes in academic articles and returns them without footnotes and citaions. DO NOT SUMMAIRIZE IT OR CHANGE ANY TEXT! do not waste time describing what you have done! be careful when dealing with things like names with abbreiations.process this text: {input}",
#          }
#     ],
#     model="gpt-4o-mini-2024-07-18",
#     #model="gpt-3.5-turbo-0125",
#     )
#
#     return chat_completion.choices[0].message.content


# asynchronous wrapper functions
async def remove_references_async(input_text):

    return await asyncio.to_thread(remove_references, input_text)

async def ai_remove_footnotesNcites_async(input_text):
# if necessary built check for splitting it up if it exceeds a context window max - 4o mini is 128,000 tokens
    #word_count = word_tokenize(input_text)
    #if len(word_count) > x000:
    #    return await asyncio.to_thread(long_ai_rem_footcite, input_text)
    return await asyncio.to_thread(ai_rem_footcite, input_text)   #(ai_remove_footnotesNcites, input_text)





