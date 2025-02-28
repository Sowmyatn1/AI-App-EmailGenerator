import streamlit as st
from openai import OpenAI
import os
import sys
import io


api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

client = OpenAI(api_key=api_key)

def GenerateEmailFromOpenAI(user_input):
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages=[
            {"role":"system","content":"you are a helpful assistant that generates professional emails."},
            {"role": "user", "content": f"write an email about :{user_input}"},
        ],
        max_tokens = 150,
        temperature = 0.7
     )

    return response.choices[0].message.content.strip()

st.title("Email Generator APP")
st.write("Enter your prompt here")
user_input= st.text_area("prompt")


if st.button("Generate Email"):
    geerated_email = GenerateEmailFromOpenAI(user_input)
    st.write(f"Generated email BAsed on:{geerated_email}")
