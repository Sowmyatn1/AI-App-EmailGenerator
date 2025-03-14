import streamlit as st
import os
#import mysql.connector
from sqlalchemy import create_engine, text
#from mysql.connector import Error
from dotenv import load_dotenv
from urllib.parse import quote_plus
from llm_agent import initialize_sql_agent 
from generate_email import GenerateEmailFromOpenAI
from sqlalchemy.exc import SQLAlchemyError


# Set Streamlit page configuration
st.set_page_config(page_title="SQL Genie: Ask & Query! – Fun and interactive.")

#this code belongs to sql db query and generating email project .make sure below files are in the project
#generate_email.py,llm_agent.py,sqlapp.py


# Clear previous session state
if 'session_initialized' not in st.session_state:
    # Clear previous session state
    for key in list(st.session_state.keys()):
        if key != 'session_initialized':
            if key in st.session_state:
                del st.session_state[key]
    st.session_state.session_initialized = True
    st.session_state.query = None
    st.session_state.query_result = None
    st.session_state.db_connected = False
    st.session_state.email_generated = False
    st.session_state.emailquery = False


# Load environment variables from .env file
load_dotenv()

# Load configuration values from the environment
api_key = os.getenv("OPENAI_API_KEY")
db_config = {
    "host":os.getenv("DB_host"),
    "user":os.getenv("DB_user"),
    "password": os.getenv("DB_password"),
    "database": os.getenv("DB_database"),
    "port": os.getenv("DB_port")
}

# URL-encode the password to handle special characters like '@'
encoded_password = quote_plus(db_config['password'])

# Set the db_config with the encoded password
db_config['password'] = encoded_password

# Check if API key is missing
if api_key is None:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()



if "db_config" not in st.session_state:
    st.session_state.db_config = db_config

if "db_connected" not in st.session_state:
    st.session_state.db_connected = False

def test_connection(config):
    """Test database connection"""
    try:
        # Test connection using SQLAlchemy
        connection_string = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        print(f"Connection string: {connection_string}")
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("SQLAlchemy connection successful")
        return True # Connection successful
   
    except SQLAlchemyError as e:
        print(f"Database connection error: {e}")
        return False

    #return False


# Call the function to test the connection
if st.button("Test Database Connection"):
    success = test_connection(st.session_state.db_config)
    if success:
        st.success("Database connection successful!")
        st.session_state.db_connected = True

        try:
            # call the method initialize_sql_agent from llm_agent.py
            st.session_state.sql_agent = initialize_sql_agent(st.session_state.db_config)
            st.success("✅ SQL Agent Initialized Successfully!")
        except Exception as e:
            st.error(f"❌ Failed to initialize SQL Agent: {str(e)}")
            st.session_state.sql_agent = None

    else:
        st.error("Database connection failed. Check credentials.")
        st.session_state.db_connected = False


# SQL Query Execution Section
st.subheader("🔍 Enter your question to interact with the Database:")

if "query" not in st.session_state:
    st.session_state.query = None

#st.session_state.query = st.text_area("Type your question here:")
#user_input = st.text_area("Type your question here:", value=st.session_state.query if "query" in st.session_state else "")
user_input = st.text_area(
    "Type your question here:", 
    key="user_input_area",  # Adding a specific key
    value=st.session_state.get("query", "")  # Default to empty string if not in session
)



# To prevent query being re-executed on button click every time, store the result in session state
if "query_result" not in st.session_state:
    st.session_state.query_result = None


submit_button_clicked = st.button("Submit")

if submit_button_clicked:
    print("inside submit query")
    st.session_state.query = user_input 
    if not st.session_state.query.strip():
        st.warning("⚠️ Please enter a query.")
    elif not st.session_state.db_connected or not st.session_state.sql_agent:
        st.error("❌ No active database connection or SQL Agent not initialized.")
    else:
        if user_input != st.session_state.query:
            st.session_state.query = user_input
        with st.spinner("Processing your query..."):
            try:
                print(f"Processing the user query in next step : {st.session_state.query}")
                response = st.session_state.sql_agent.run(st.session_state.query)
                #save result in session
                st.session_state.query_result = response 
                #st.subheader("🔹 Query Result:")
                #st.code(response, language="sql")
                st.session_state.email_generated = False
                st.session_state.emailquery=st.session_state.query 
            except Exception as e:
                st.error(f"❌ Error executing query: {str(e)}")

# Always display the query result if available
if st.session_state.get("query_result"):
     st.subheader("🔹 Query Result:")
     st.code(st.session_state.query_result, language="sql")


# clear the query once its executed this will avoid the execution of old query
st.session_state.query = None


# Check if "Generate Email" button was clicked and use session_state to track it
if 'email_generated' not in st.session_state:
    st.session_state.email_generated = False

if st.session_state.query_result and 'email' in st.session_state.emailquery.lower():
    email_type = st.selectbox("Select email type", ["Discount", "Product Recommendation", "Purchase Appreciation", "Other"])

        # Only show Generate Email button once the query has been processed
    if st.button("Generate Email"):
        st.session_state.email_generated = True
        st.write("⏳ Generating email for your query...")
        user_input = f"Generate a {email_type} email for the email ids {st.session_state.query_result}"
        email_tone = "Formal"
        email_length= "Medium"
        with st.spinner("🤖 AI is generating your email..."):
            st.session_state.email_content = GenerateEmailFromOpenAI(user_input, email_tone, email_length, email_type)
        
        st.success("✅ Email generated successfully!")
       
        
    if st.session_state.email_generated:
        
        #st.write(st.session_state.email_content)
        #st.text_area("✏️ Copy Email:", st.session_state.email_content, height=200)
        email_content = st.session_state.email_content
        print(f"email content :{email_content}")
        # Extract the subject line (e.g., "subject: Exclusive Discount Offer for You")
        subject_line = ""
        if "subject:" in email_content.lower():
            subject_line = email_content.split("Subject:")[1].split("\n")[0].strip()
        
        # extract email body
        email_body = email_content.split("\n", 1)[1].strip() 

        st.subheader("Generated Email Template:")
        # To: Show the email IDs (names in this case)
        st.markdown(f"**To:** {st.session_state.query_result}")
        st.markdown(f"---")
        st.markdown(f"**Subject:** {subject_line}")
        st.markdown(f"---")
        # Email Content: Display the email body
        #st.markdown(f"**email_body:**")
        #st.markdown(f"<div style='padding-left: 20px;'>Dear Customer,</div>", unsafe_allow_html=True)
        st.markdown(f"{email_body}")
        st.session_state.email_generated = False  # Reset after showing email

