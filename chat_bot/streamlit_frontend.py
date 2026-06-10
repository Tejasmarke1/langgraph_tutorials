import streamlit as st   
from langchain.messages import HumanMessage
from langgraph_backend import chatbot 
config1={"configurable":{"thread_id":"2"}}
st.title("Echo Bot")



if "messages" not in st.session_state:
    st.session_state.messages = []
    


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        

user_input=st.chat_input('Type here')



if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message('user'):
        st.text(user_input)
    # Display assistant response in chat message container
    response = chatbot.invoke({'messages':HumanMessage(content=user_input)},config=config1)
    ai_message=response['messages'][-1].content
    with st.chat_message("assistant"):
        st.markdown(ai_message)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": ai_message})
        
        
        

        
    
    
