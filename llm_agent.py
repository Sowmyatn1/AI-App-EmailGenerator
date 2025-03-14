
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory 
from langchain_community.chat_message_histories import SQLChatMessageHistory 
import os


""" this code belongs to sql db query and generating email project .make sure below files are in the project
generate_email.py,llm_agent.py,sqlapp.py"""


"""Provides instructions to the AI agent on how to query the database"""

CUSTOM_SUFFIX = """Begin!

Relevant pieces of previous conversation:
{chat_history}
(Note: Only reference this information if it is relevant to the current query.)

Question: {input}
Thought Process: It is imperative that I do not fabricate information not present in any table or engage in hallucination; maintaining trustworthiness is crucial.
In SQL queries involving string or TEXT comparisons like first_name, I must use the `LOWER()` function for case-insensitive comparisons and the `LIKE` operator for fuzzy matching. 

I will only work with the following tables:
- customer
- orders
- message_store
If the query involves any other tables, I must disregard it and reframe the query using only the allowed tables.

Make sure that query is related to the SQL database and tables you are working with.
If the result is empty, the Answer should be "No results found". DO NOT hallucinate an answer if there is no result.

My final response should STRICTLY be the output of SQL query.

{agent_scratchpad}
"""


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

"""This function sets up the SQL agent for querying the database.
1. Validate Database Configuration
2. Create OpenAI Chat Model
3. Build MySQL Connection URL
4. Connect to Database
5. Create SQL Toolkit which allows the LLM to interact with the SQL database.
6. Store Chat History in SQL Database
7. Create the SQL Agent initializes and configures a LangChain SQL Agent that interacts with a MySQL database using OpenAI's gpt-3.5-turbo.

"""
def initialize_sql_agent(db_config):
    print("inside initialize sql agent")
    required_fields = ['user', 'password', 'host', 'database', 'port']
    if not db_config or not isinstance(db_config, dict):
        raise ValueError("Invalid database configuration")
        
    # Check required fields
    for field in required_fields:
        if field not in db_config or not db_config[field]:
            raise ValueError(f"Missing required field: {field}")


    try:
        print("the dbconfig has all the required fileds")
        llm=ChatOpenAI(
            temperature=0,
             model='gpt-3.5-turbo',
            openai_api_key=OPENAI_API_KEY
        )
        # Build the connection string dynamically
        username = db_config['user']
        password = db_config['password']
        host = db_config['host']
        port = db_config['port']
        database = db_config['database']
        print("connceting to database in llm_agent")
        db_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

        db = SQLDatabase.from_uri(db_url)
        print("connected to database in llm_agent")
        # Create toolkit with LLM
        toolkit = SQLDatabaseToolkit(
            db=db,
            llm=llm
        )

        """SQLChatMessageHistory is a utility from LangChain that allows storing chat messages in a SQL database.
        create a table "message_store" in database
        session_id_field_name="session_id" indicates that the session ID will be stored in a field named "session_id" in the database."""

        message_history = SQLChatMessageHistory(
            session_id="my-session",
            connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}",
            table_name="message_store",
            session_id_field_name="session_id"
        )   
        memory = ConversationBufferMemory(memory_key="chat_history", input_key='input', chat_memory=message_history, return_messages=False)
        print("stored chat message history sucessfully")

        """ The agent is designed to interact with an SQL database, execute queries, and maintain conversation history""" 
        # Create and return agent
        print("creating an agent now")
        return create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            input_variables=["input", "agent_scratchpad", "chat_history"], 
            suffix=CUSTOM_SUFFIX, 
            memory=memory,
            agent_executor_kwargs={"memory": memory}, 
            verbose=True,
            handle_parsing_errors=True
        )

    except Exception as e:
        raise ValueError(f"Failed to initialize SQL agent: {str(e)}")

