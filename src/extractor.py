# src/extractor.py 

import google.generativeai as genai
import json
import os
from dotenv import load_dotenv


load_dotenv()   #Loads the .env from project root
API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=API_KEY)

#We will call our AI model for this project we use gemini AI
#Here temperature is set to 0.1 for low randomness, which is good for structured data extraction
#response_mime_type is set to application/json to ensure the model returns JSON since we are not using regex to parse the response
#generation_config is used to configure the model's behavior
model = genai.GenerativeModel("gemini-3.1-flash-lite",  generation_config={
    "temperature" : 0.1,
    "response_mime_type": "application/json",
    })

# This is the instruction we send to Gemini along with the document
PROMPT = """
You are a legal document analysis assistant specializing in rental agreements.
Extract the following 6 fields from the rental agreement document provided:

1. Agreement Value       -> The monthly rent amount (number only, e.g. 4000)
2. Agreement Start Date  -> The date the agreement starts (format: DD.MM.YYYY)
3. Agreement End Date    -> The date the agreement ends (format: DD.MM.YYYY)
                             Add exactly N months to the start date to find the end month.
                            Then use the actual LAST CALENDAR DAY of that month.
                            (January=31, February=28 or 29, March=31, April=30, May=31, June=30,July=31, August=31, September=30, October=31, November=30, December=31)
                            Example: Start 05.12.2008 + 11 months → end month is November 2009 → last day = 30.11.2009
                            Example: Start 01.04.2010 + 11 months → end month is March 2011 → last day = 31.03.2011
                            NEVER invent days that don't exist (e.g. February 31 or November 31 do not exist).
                            If an end date is EXPLICITLY stated in the document, use that exact date as-is without recalculating.
4. Renewal Notice (Days) -> Number of days notice required (number only, e.g. 90)
5. Party One             -> The landlord / owner / lessor name (full name as written)
6. Party Two             -> The tenant / resident / lessee name (full name as written)

IMPORTANT RULES:
- Return ONLY a valid JSON object. No explanation, no extra text.
- Dates must always be in DD.MM.YYYY format even if written as "20th day of May 2007"
- Agreement Value must be a plain number (no currency symbol, no commas)
- If a field is not found in the document, use empty string ""
- Party names: Do NOT include titles or salutations like Mr., Mrs., Ms., Dr., Prof., Sri., Shri.
  Extract only the core person or entity name exactly as written.

Return this exact JSON structure:
{
  "Agreement Value": "",
  "Agreement Start Date": "",
  "Agreement End Date": "",
  "Renewal Notice (Days)": "",
  "Party One": "",
  "Party Two": ""
}
"""

# -------------------------
# DOCUMENT PROCESSING
# -------------------------

def extract_fields(content, content_type: str) -> dict:
    """
    content      → either a string (for DOCX) or PIL Image (for PNG)
    content_type → "text" or "image"
    Returns a dict with the 6 extracted fields.
    """

    if content_type == "text":
        #Send the document text + prompt to Our AI model
        response = model.generate_content([PROMPT, content])

    elif content_type == "image":
        #Send the image + prompt to Our AI model
        response = model.generate_content([PROMPT, content])

    raw_text = response.text.strip()



    #Parse the JSON response
    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
       # If Gemini returned something unexpected, return empty fields
       print(f"Could not parse JSON. Raw response was:\n{raw_text}")
       result = {
        "Agreement Value": "",
        "Agreement Start Date": "",
        "Agreement End Date": "",
        "Renewal Notice (Days)": "",
        "Party One": "",
        "Party Two": ""
       }
    return result
    