from pypdf import PdfReader
import os
import nltk
nltk.download('punkt')  # Download the Punkt tokenizer models if you haven't already

from nltk.tokenize import sent_tokenize

def count_sentences(text):
    sentences = sent_tokenize(text)
    return len(sentences)

def count_lines(text):
     newline_count = 0
     for char in text:
          if char == "\n":
               newline_count += 1
     return newline_count

def pdfProcess(file_path):
     ret_text = ""
     reader = PdfReader(file_path)

     for i in range(0, len(reader.pages)):
          page = reader.pages[i]
          ret_text += page.extract_text()

     if count_sentences(ret_text) < count_lines(ret_text):
          ret_text = ret_text.replace("\n", " ")
     os.remove(file_path)
     return ret_text#

