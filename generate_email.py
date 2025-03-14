import streamlit as st
from openai import OpenAI
import os
import sys
import io
from dotenv import load_dotenv

""" this code belongs to sql db query and generating email project .make sure below files are in the project
generate_email.py,llm_agent.py,sqlapp.py"""

# Load environment variables from .env file
load_dotenv() 

api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

client = OpenAI(api_key=api_key)



def GenerateEmailFromOpenAI(user_input, email_tone, email_length, email_purpose):
    # This code is to make assign the tokens based on length of email the user wants
    Length_tokens= {"Short":150,"Medium":350,"Long":500}
    Tokens_required= Length_tokens[email_length]

   
   # asterisks are being used to emphasize that particular instruction to the AI model
    prompt = f"""Generate a well-structured professional email with the following details:
    - **Topic:** {user_input}
    - **Tone:** {email_tone}
    - **Length:** {email_length}
    - **Purpose:** {email_purpose}
    
    Ensure the email:
    - has a subject in the first line starting with subject:
    - Begins with "Dear Customer,"
    - Ends with "Thanks and Regards, [Your Name]"
    - Is **concise yet complete** (no unfinished sentences)
    - Is professional and well-structured
    """
 
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates professional emails."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=Tokens_required,
        temperature=0.7
    )
    print(response.choices[0].finish_reason)
    return response.choices[0].message.content.strip()  