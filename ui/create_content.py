import streamlit as st
import random
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from graph.slide_graph import SlideGraph
from integration.slash_command_runner import run_slash_command

st.title("Create Content")

def get_file_contents(uploaded_file):
        file_contents = uploaded_file.read()
        return file_contents

def get_message_history(messages):
    message_history = []
    for m in messages:
        if m["role"] == "user":
            message_history.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            message_history.append(AIMessage(content=m["content"]))
    return message_history

def show_chat_ui():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "thread-id" not in st.session_state:
        st.session_state.thread_id = random.randint(1000, 9999)
    thread_id = st.session_state.thread_id

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    if prompt := st.chat_input("What slides do you want to generate today?", accept_file=True, file_type=["py", "js", "md", "txt"]):
        if prompt and prompt["files"]:
            uploaded_file=prompt["files"][0]
            file_contents = get_file_contents(uploaded_file)
            prompt.text += f"\n\nHere is the content of the uploaded file {uploaded_file.name}:\n```\n{file_contents.decode('utf-8')}\n```"
    
        user_prompt = prompt.text
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        
        with st.chat_message("user"):
            st.write(user_prompt)

        runGraph = SlideGraph(st.secrets['OPENAI_MODEL_NAME'],st.secrets['OPENAI_API_KEY'])
        with st.spinner("Thinking ...", show_time=True):
            full_response = ""
            params={'message_history': get_message_history(st.session_state.messages),"user_prompt":user_prompt}
            if st.session_state.get("slide_content"):
                params['slide_content'] = st.session_state.get("slide_content")
            
            for s in runGraph.graph.stream(params, {"configurable":{"thread_id":thread_id}}):
                #print(f"GRAPH RUN: {s}")
                for k,v in s.items():
                    print(f"\n\nDEBUG DEBUG Key: {k}, Value: {v}")
                
                    if resp := v.get("incremental_response"):
                        with st.chat_message("assistant"):
                            placeholder = st.empty()
                            for response in resp:
                                if isinstance(response, dict) and "content" in response:    
                                    full_response = full_response + response["content"]
                                else:
                                    full_response = full_response + getattr(response, 'content', str(response))
                                placeholder.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    if resp := v.get("final_response"):
                        full_response = resp
                        print(f"\n\nDEBUG DDEBUG DEBUG. Final full response: {full_response}")
                        with st.chat_message("assistant"):
                            st.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    if resp := v.get("expanded_response"):
                        print(f"\n\nDEBUG DE. Expanded response: {resp}")
                        with st.sidebar.expander("Detailed output"):
                            st.markdown(f"{resp}")
                    if resp := v.get("slide_content"):
                        print(f"\n\nDEBUG DE. Adding to Session State the Slide content: {resp}")
                        st.session_state["slide_content"] = resp

if __name__ == "__main__":
    show_chat_ui()
