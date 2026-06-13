import streamlit as st   
from langchain.messages import HumanMessage
from langgraph_database_backend import chatbot,retrive_all_threads,naming_llm,load_chat_names,save_chat_name
import uuid

def generate_thread_id():
    thread_id=uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id=generate_thread_id()
    st.session_state['thread_id']=thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['messages']=[]
    
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].insert(0, thread_id) 
        st.session_state['chat_names'][thread_id] = "New Chat" 
        
def load_conversation(thread_id):
    state=chatbot.get_state(config={"configurable":{"thread_id":thread_id}})
    return state.values.get("messages",[])


def get_chat_name(user_input):
    response = naming_llm.invoke([
        HumanMessage(content=f"Give a 4-word title for a chat starting with: {user_input}. Reply with only the title, no punctuation.")
    ])
    return response.content.strip()
    
    
    


if "messages" not in st.session_state:
    st.session_state['messages'] = []
    
if "thread_id" not in st.session_state:
    st.session_state['thread_id']=generate_thread_id()
    
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=retrive_all_threads()
    
if 'chat_names' not in st.session_state:
    st.session_state['chat_names'] = load_chat_names()
    
    
add_thread(st.session_state['thread_id'])
    
    
    
st.sidebar.title("Chatbot")


if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")

for thread_id in st.session_state['chat_threads']:
    name = st.session_state['chat_names'].get(thread_id, "New Chat")
    is_active = thread_id == st.session_state['thread_id']
    
    label = f"💬 **{name}**" if is_active else f"💬 {name}"
    if st.sidebar.button(label,key=str(thread_id)):
        st.session_state['thread_id']=thread_id
        messages=load_conversation(thread_id)
        
        
        temp_messages=[]
        
        for message in messages:
            if isinstance(message,HumanMessage):
                role='user'
            else:
                role='assistant' 
            temp_messages.append({'role':role,'content':message.content})

        
        st.session_state['messages']=temp_messages 
        


for message in st.session_state['messages']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        

user_input=st.chat_input('Type here')



if user_input:
    # Set chat name from first user message
    current_thread = st.session_state['thread_id']
    if st.session_state['chat_names'].get(current_thread) == "New Chat":
        name = get_chat_name(user_input)
        st.session_state['chat_names'][current_thread] = name
        save_chat_name(str(current_thread),name)
        
    st.session_state['messages'].append({"role": "user", "content": user_input})
    with st.chat_message('user'):
        st.text(user_input)
    # Display assistant response in chat message container
    
    CONFIG={"configurable":{"thread_id":st.session_state['thread_id']}}
    with st.chat_message('assistant'):
    
        ai_message=st.write_stream(
            message_chunk.content for message_chunk,metadata in chatbot.stream(
                {
                    "messages": [
                    HumanMessage(content=user_input)
                    ]
                },
                config=CONFIG,
                stream_mode='messages',
                version='v2'
            ) 
            if message_chunk.content
        ) 
    # Add assistant response to chat history
    st.session_state['messages'].append({"role": "assistant", "content": ai_message})
        
        
        

        
    
    
