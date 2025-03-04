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

def GenerateEmailFromOpenAI(user_input, email_tone, email_length, email_purpose):
    # This code is to make assign the tokens based on length of email the user wants
    Length_tokens= {"Short":50,"Medium":100,"Long":200}
    Tokens_required= Length_tokens[email_length]
    prompt = f"""Write an email about: {user_input} 
    - Tone: {email_tone} 
    - Length: {email_length} 
    - Purpose: {email_purpose} 
    Make it professional and well-structured.Begin email with Dear[name] add Thanks and reagrds section at the end"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates professional emails."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=Tokens_required,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()  

st.title("Email Generator APP")
st.write("Enter your prompt here")
user_input= st.text_area("prompt")

# Sidebar for user input customization
st.sidebar.header("Customize Email")
email_tone = st.sidebar.selectbox("Select Tone", ["Formal", "Casual", "Professional"])
email_length = st.sidebar.radio("Select Length", ["Short", "Medium", "Long"])
email_purpose = st.sidebar.selectbox("Email Type", ["Job Application", "Customer Service", "Sales Pitch"])


if st.button("Generate Email"):
    with st.spinner("Generating your email..."):
        try:
            generated_email = GenerateEmailFromOpenAI(user_input,email_tone,email_length,email_purpose)
            st.markdown(f"### ✉️ Generated Email")
            st.markdown(f"**Tone:** {email_tone}")
            st.markdown(f"**Length:** {email_length}")
            st.markdown(f"---")
            st.write(generated_email)

        except Exception as e:
            st.error("⚠️ Error generating email. Please try again.")



