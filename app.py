import streamlit as st
from openai import OpenAI
import os
import sys
import io
from dotenv import load_dotenv
import PyPDF2



#this file has code which will take user question and generate  email for that.yhis is a standalone code which has a UI to display the result 
#run this as a streamlit run app.py 

# Load environment variables from .env file
load_dotenv() 

# the OPENAI_API_KEY is stored in .env file .fetch it deom env file
api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

client = OpenAI(api_key=api_key)



def extract_text_from_resume(uploaded_file):
    """Extract text from a PDF resume."""
    if uploaded_file is not None:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text
    return ""




#the below method will generate a email for user question . we are using gpt LLM for this purpose

def GenerateEmailFromOpenAI(user_input, email_tone, email_length, email_purpose,resume_text=""):
    # This line is to make assign the tokens based on length of email the user wants
    Length_tokens= {"Short":150,"Medium":350,"Long":500}
    Tokens_required= Length_tokens[email_length]

   
   # asterisks are being used to emphasize that particular instruction to the AI model
    prompt = f"""Generate a well-structured professional email with the following details:
    - **Topic:** {st.session_state.user_input}
    - **Tone:** {email_tone}
    - **Length:** {email_length}
    - **Purpose:** {email_purpose}
    """
    
    if email_purpose == "Job Application" and resume_text:
        prompt += f"""
        - **Resume Details:** Use the following details from my resume to strengthen the email:
        {resume_text[:1000]}  # Limit resume text to 1000 characters for brevity
        """
    
    prompt += """
    Ensure the email:
    - Begins with "Dear [Name],"
    - Ends with "Thanks and Regards, [Your Name]"
    - Is **concise yet complete** (no unfinished sentences)
    - Is professional and well-structured
    - The email should not be cut off midway and should provide a complete message within the specified length
    - If necessary, adjust the content to meet the token limit without losing meaning.
    - If you reach the token limit, gracefully truncate at a logical stopping point without breaking sentences.
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
    #print(response.choices[0].finish_reason)
    return response.choices[0].message.content.strip()  


# Below method will generate interview questions based on the job description


def GenerateInterviewQuestions(job_description,resume_text=""):
    print("inside generate interview questions")
    prompt = f"""Generate a list of interview questions based on the following job description:
    {job_description}
    """
    
    if resume_text:
        prompt += f"""
        - **Candidate's Experience:**
        {resume_text[:1000]}
        """
    
    prompt += """
    Ensure the questions are relevant to the role and the candidate's experience.
    Provide at least 5 questions.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert interviewer generating relevant interview questions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

st.title("Email Generator APP")
#st.write("Enter your prompt here")
user_input= st.text_area("Prompt (describe what you want in the email)")
# save user input in session variable
if user_input:
    st.session_state.user_input = user_input
# Sidebar for user input customization
st.sidebar.header("Customize Email")
email_tone = st.sidebar.selectbox("Select Tone", ["Formal", "Casual", "Professional"])
email_length = st.sidebar.radio("Select Length", ["Short", "Medium", "Long"])
email_purpose = st.sidebar.selectbox("Email Type", ["Job Application", "Customer Service", "Welcome Email","Event Invitation Email","Feedback Request Email"])


resume_text = ""
if email_purpose == "Job Application":
    uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])
    if uploaded_file is not None:
        resume_text = extract_text_from_resume(uploaded_file)




if st.button("Generate Email"):

    if not st.session_state.user_input:
        st.warning("Please enter a prompt describing what you want in the email.")
        """Please enter a prompt describing what you want in the email."""
    else:
        with st.spinner("Generating your email..."):
            try:
                generated_email = GenerateEmailFromOpenAI( st.session_state.user_input,email_tone,email_length,email_purpose,resume_text)

                st.markdown(f"### ✉️ Generated Email")
                st.markdown(f"**Tone:** {email_tone}")
                st.markdown(f"**Length:** {email_length}")
                st.markdown(f"---")
                st.write(generated_email)
                #st.markdown(f"Thanks and Regards [Name]")
                
            except Exception as e:
                st.error("⚠️ Error generating email. Please try again.")


if st.button("Generate Interview Questions"):
    if not st.session_state.user_input:
        st.warning("Please enter the job description to generate interview questions.")
    else:
        with st.spinner("Generating interview questions..."):
            try:
                #print(f"resume text : {resume_text}")
                interview_questions = GenerateInterviewQuestions( st.session_state.user_input, resume_text)
                st.markdown("### 🤔 Interview Questions")
                st.write(interview_questions)
            except Exception as e:
                st.error("⚠️ Error generating interview questions. Please try again.")
