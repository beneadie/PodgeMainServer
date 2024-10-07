from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI, Schema, File
from ninja.files import UploadedFile
#from django.core.files.uploadedfile import TemporaryUploadedFile
from . import textProcess
from . import urlToText
from . import PdfProcess
import os
import tempfile


TextAPI = NinjaAPI(urls_namespace='TextAPI')

#class PDF_request(Schema):
#    pdf: str

class URL_convert(Schema):
     url: str

class Cite_with_text(Schema):
     txt: str

class Text_footnotesandcites(Schema):
     txt : str

@TextAPI.post("/urltotxt")
def urltotxt(request, urlreq: URL_convert):
     try:
          return urlToText.extract_text_from_article(urlreq.url)
     except Exception as e:
          return {"error": str(e)}

@TextAPI.post("/removeCitations")
async def removeCitations_async(request, cwt: Cite_with_text):
     try:
          ret_text = await textProcess.remove_references_async(cwt.txt)
          return ret_text
     except Exception as e:
          return {"error": str(e)}

@TextAPI.post("/removeCitesandFootnotesAI")
async def removeCitesandFootnotesAI(request, textdata :Text_footnotesandcites):
     try:
          ret_text = await textProcess.ai_remove_footnotesNcites_async(textdata.txt)
          return ret_text
     except Exception as e:
          return {"error": str(e)}



# come back to these later
# might be able to do them in javascript
@TextAPI.post("/pdfConvertTxt")
def pdfConvert(request, file: UploadedFile = File(...)):
    if file:
        try:
            # Save the uploaded file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)

            # Process the PDF file
            text = PdfProcess.pdfProcess(temp_file.name)

            # Return the extracted text
            return {"text": text}
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"error": "No file provided"}
