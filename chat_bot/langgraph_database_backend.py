from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3

load_dotenv()


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7,streaming=True)
naming_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}


conn=sqlite3.connect(database='chatbot.db',check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)


graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrive_all_threads():
    seen = {}
    for checkpoint in checkpointer.list(None):
        tid = checkpoint.config['configurable']['thread_id']
        ts = checkpoint.metadata.get('created_at', '')
        if tid not in seen or ts > seen[tid]:
            seen[tid] = ts
    return sorted(seen.keys(), key=lambda t: seen[t],reverse=True)


def init_chat_names_table():
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_names (
            thread_id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)
    conn.commit()

def save_chat_name(thread_id: str, name: str):
    conn.execute(
        "INSERT OR REPLACE INTO chat_names (thread_id, name) VALUES (?, ?)",
        (str(thread_id), name)
    )
    conn.commit()

def load_chat_names() -> dict:
    cursor = conn.execute("SELECT thread_id, name FROM chat_names")
    return {row[0]: row[1] for row in cursor.fetchall()}

init_chat_names_table()