import requests
from bs4 import BeautifulSoup

def extract_text_from_article(url):
     try:
          # Send a GET request to the article URL
          response = requests.get(url)

          # Check if the request was successful
          if response.status_code == 200:
               # Parse the HTML content of the article page
               soup = BeautifulSoup(response.content, 'html.parser')

               # Extract text from <p> tags or any other tags containing the article content
               article_text = '\n'.join([p.get_text() for p in soup.find_all('p')])

               return article_text
          else:
               #print("Failed to fetch article:", response.status_code)
               return f"""Failed to fetch article.
Error Code: {response.status_code}"""
     except:
          return "URL was not valid"
