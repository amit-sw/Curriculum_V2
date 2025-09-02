import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI

from utils.prompt_manager import get_prompt
from integration.supabase_integration import get_supabase_client, add_brainstorm_to_db
from utils.llm_calls import run_model

def get_file_contents(uploaded_file):
        file_contents = uploaded_file.read()
        return file_contents
    
def create_llm_msg(system_prompt: str, messageHistory: list[BaseMessage]):
    resp = []
    resp.append(SystemMessage(content=system_prompt))
    resp.extend(messageHistory)
    return resp

def get_last_assistant_message(messageHistory: list[dict]):
    for m in reversed(messageHistory):
        if m["role"] == "assistant":
            return m["content"]
    return ""

def save_brainstorm(command, arg_msg, last_assistant_msg):
    print(f"SAVE-BRAINSTORM: Ignoring the detected {command=} with {arg_msg=}, \n\n\n{last_assistant_msg[:100]=}")
    supabase=get_supabase_client()
    add_brainstorm_to_db(supabase, arg_msg, last_assistant_msg)
    #
    
def run_slash_command(command, arg_msg, msg_history, slide_content):
    last_assistant_msg = get_last_assistant_message(msg_history)
    if command.lower() == "/save":
        save_brainstorm(command, arg_msg, last_assistant_msg)
    else:
        print(f"RUN-SLASH-COMMAND: Ignoring the detected {command=} with {arg_msg=}, \n\n\n {slide_content=}\n\n\n{last_assistant_msg[:100]=}")
        # run_slash_command(command, args, st.session_state.brainstormmessages, st.session_state.get("slide_content", {}))
    return  

def get_message_history(messages):
    message_history = []
    for m in messages:
        if m["role"] == "user":
            message_history.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            message_history.append(AIMessage(content=m["content"]))
    return message_history

def show_sidebar_save_info():
    command="/save"
    messages=st.session_state.get("brainstormmessages", [])
    last_assistant_msg=get_last_assistant_message(messages)
    if len(last_assistant_msg)<10:
        return
    with st.sidebar:
        st.divider()
        bname=st.text_input("Name")
        if st.button("Save"):
            save_brainstorm(command, bname, last_assistant_msg)

def show_chat_ui():
    if "brainstormmessages" not in st.session_state:
        st.session_state.brainstormmessages = []

    for message in st.session_state.brainstormmessages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    show_sidebar_save_info()
    
    if prompt := st.chat_input("What content do you want to brainstorm today?", accept_file=True, file_type=["py", "js", "md", "txt"]):
        if prompt and prompt["files"]:
            uploaded_file=prompt["files"][0]
            file_contents = get_file_contents(uploaded_file)
            prompt.text += f"\n\nHere is the content of the uploaded file {uploaded_file.name}:\n```\n{file_contents.decode('utf-8')}\n```"
    
        user_prompt = prompt.text
        st.session_state.brainstormmessages.append({"role": "user", "content": user_prompt})
        
        with st.chat_message("user"):
            st.write(user_prompt)
        
        print(f"USER PROMPT: {user_prompt=}, That is all.")    
        if user_prompt.startswith("/"):
            command = user_prompt.split(" ")[0]
            args = user_prompt[len(command):].strip()
            print(f"Ignoring the detected command: {command} with args: {args}")
            run_slash_command(command, args, st.session_state.brainstormmessages, st.session_state.get("slide_content", {}))
            return

        with st.spinner("Thinking ...", show_time=True):
            reasoning = {"effort":"low","summary":None}
            model = ChatOpenAI(model=st.secrets['OPENAI_MODEL_NAME'], api_key=st.secrets['OPENAI_API_KEY'], reasoning=reasoning)
            llm_messages = create_llm_msg(get_prompt("brainstorm_content"), get_message_history(st.session_state.brainstormmessages))
            returned_string,full_response_from_llm = run_model(model, llm_messages)
            with st.chat_message("assistant"):
                st.markdown(returned_string)
            st.session_state.brainstormmessages.append({"role": "assistant", "content": returned_string})

if __name__ == "__main__":
    show_chat_ui()