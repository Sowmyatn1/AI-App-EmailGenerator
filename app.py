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
    Length_tokens= {"Short":150,"Medium":350,"Long":500}
    Tokens_required= Length_tokens[email_length]

   
   # asterisks are being used to emphasize that particular instruction to the AI model
    prompt = f"""Generate a well-structured professional email with the following details:
    - **Topic:** {user_input}
    - **Tone:** {email_tone}
    - **Length:** {email_length}
    - **Purpose:** {email_purpose}
    
    Ensure the email:
    - Begins with "Dear [Name],"
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

st.title("Email Generator APP")
st.write("Enter your prompt here")
user_input= st.text_area("Prompt (describe what you want in the email)")

# Sidebar for user input customization
st.sidebar.header("Customize Email")
email_tone = st.sidebar.selectbox("Select Tone", ["Formal", "Casual", "Professional"])
email_length = st.sidebar.radio("Select Length", ["Short", "Medium", "Long"])
email_purpose = st.sidebar.selectbox("Email Type", ["Job Application", "Customer Service", "Welcome Email","Event Invitation Email","Feedback Request Email"])


if st.button("Generate Email"):

    if not user_input:
        st.warning("Please enter a prompt describing what you want in the email.")
        """Please enter a prompt describing what you want in the email."""
    else:
        with st.spinner("Generating your email..."):
            try:
                generated_email = GenerateEmailFromOpenAI(user_input,email_tone,email_length,email_purpose)

                st.markdown(f"### ✉️ Generated Email")
                st.markdown(f"**Tone:** {email_tone}")
                st.markdown(f"**Length:** {email_length}")
                st.markdown(f"---")
                st.write(generated_email)
                st.markdown(f"Thanks and Regards [Name]")

            except Exception as e:
                st.error("⚠️ Error generating email. Please try again.")



