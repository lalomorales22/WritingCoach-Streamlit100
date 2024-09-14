import streamlit as st
import ollama
import time
import json
import os
from datetime import datetime
from openai import OpenAI

# List of available models
MODELS = [
    "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo",  # OpenAI models
    "llama3.1:8b", "gemma2:2b", "mistral-nemo:latest", "phi3:latest",  # Ollama models
]

# Writing types and feedback categories
WRITING_TYPES = [
    "Essay", "Creative Writing", "Technical Writing", "Journalism",
    "Academic Paper", "Business Writing", "Blog Post", "Script"
]

FEEDBACK_CATEGORIES = [
    "Grammar", "Style", "Structure", "Clarity", "Coherence",
    "Vocabulary", "Tone", "Argumentation"
]

def get_ai_response(messages, model):
    if model.startswith("gpt-"):
        return get_openai_response(messages, model)
    else:
        return get_ollama_response(messages, model)

def get_openai_response(messages, model):
    client = OpenAI()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content, response.usage.prompt_tokens, response.usage.completion_tokens
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None, 0, 0

def get_ollama_response(messages, model):
    try:
        response = ollama.chat(
            model=model,
            messages=messages
        )
        return response['message']['content'], response['prompt_eval_count'], response['eval_count']
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None, 0, 0

def stream_response(messages, model):
    if model.startswith("gpt-"):
        return stream_openai_response(messages, model)
    else:
        return stream_ollama_response(messages, model)

def stream_openai_response(messages, model):
    client = OpenAI()
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )
        return stream
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def stream_ollama_response(messages, model):
    try:
        stream = ollama.chat(
            model=model,
            messages=messages,
            stream=True
        )
        return stream
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def save_writing_session(messages, filename):
    session = {
        "timestamp": datetime.now().isoformat(),
        "messages": messages
    }
    
    os.makedirs('writing_sessions', exist_ok=True)
    file_path = os.path.join('writing_sessions', filename)
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                sessions = json.load(f)
        else:
            sessions = []
    except json.JSONDecodeError:
        sessions = []
    
    sessions.append(session)
    
    with open(file_path, 'w') as f:
        json.dump(sessions, f, indent=2)

def load_writing_sessions(uploaded_file):
    if uploaded_file is not None:
        try:
            sessions = json.loads(uploaded_file.getvalue().decode("utf-8"))
            return sessions
        except json.JSONDecodeError:
            st.error(f"Error decoding the uploaded file. The file may be corrupted or not in JSON format.")
            return []
    else:
        st.warning("No file was uploaded.")
        return []

def main():
    st.set_page_config(layout="wide")
    st.title("Writing Coach: Real-time Feedback on Writing Style, Grammar, and Structure")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "token_count" not in st.session_state:
        st.session_state.token_count = {"prompt": 0, "completion": 0}

    if "user_name" not in st.session_state:
        st.session_state.user_name = "Writer"

    st.session_state.user_name = st.text_input("Enter your name:", value=st.session_state.user_name)

    st.sidebar.title("Writing Coach Settings")
    model = st.sidebar.selectbox("Choose a model", MODELS)

    custom_instructions = st.sidebar.text_area("Custom Instructions", 
        """You are an advanced Writing Coach AI. Your role is to provide real-time feedback on writing style, grammar, and structure. You should offer constructive criticism, suggestions for improvement, and explanations of writing principles to help users enhance their writing skills.

Your capabilities include:
1. Analyzing grammar and syntax
2. Evaluating writing style and tone
3. Assessing document structure and flow
4. Providing feedback on clarity and coherence
5. Suggesting improvements in vocabulary and word choice
6. Offering insights on argumentation and persuasion techniques

When providing feedback:
- Be constructive and encouraging
- Explain the reasoning behind your suggestions
- Provide specific examples and alternatives
- Tailor your feedback to the chosen writing type
- Prioritize the most impactful improvements
- Acknowledge strengths as well as areas for improvement

Remember, your goal is to help users improve their writing skills across various types of writing, from creative to academic and professional contexts.""")

    writing_type = st.sidebar.selectbox("Choose writing type", WRITING_TYPES)
    feedback_focus = st.sidebar.multiselect("Select feedback focus", FEEDBACK_CATEGORIES, default=FEEDBACK_CATEGORIES)

    theme = st.sidebar.selectbox("Choose a theme", ["Light", "Dark"])
    if theme == "Dark":
        st.markdown("""
        <style>
        .stApp {
            background-color: #1E1E1E;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)

    if st.sidebar.button("Start New Writing Session"):
        st.session_state.messages = []
        st.session_state.token_count = {"prompt": 0, "completion": 0}

    st.sidebar.subheader("Session Management")
    save_name = st.sidebar.text_input("Save session as:", f"{writing_type.lower()}_writing_session.json")
    if st.sidebar.button("Save Writing Session"):
        save_writing_session(st.session_state.messages, save_name)
        st.sidebar.success(f"Session saved to writing_sessions/{save_name}")

    st.sidebar.subheader("Load Writing Session")
    uploaded_file = st.sidebar.file_uploader("Choose a file to load sessions", type=["json"], key="session_uploader")
    
    if uploaded_file is not None:
        try:
            sessions = load_writing_sessions(uploaded_file)
            if sessions:
                st.sidebar.success(f"Loaded {len(sessions)} sessions from the uploaded file")
                selected_session = st.sidebar.selectbox(
                    "Select a session to load",
                    range(len(sessions)),
                    format_func=lambda i: sessions[i]['timestamp']
                )
                if st.sidebar.button("Load Selected Session"):
                    st.session_state.messages = sessions[selected_session]['messages']
                    st.sidebar.success("Writing session loaded successfully!")
            else:
                st.sidebar.error("No valid writing sessions found in the uploaded file.")
        except Exception as e:
            st.sidebar.error(f"Error loading writing sessions: {str(e)}")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.text_area("Enter your text for feedback:", height=200):
        st.session_state.messages.append({"role": "user", "content": f"{st.session_state.user_name}: {prompt}"})
        with st.chat_message("user"):
            st.markdown(f"{st.session_state.user_name}: {prompt}")

        type_instruction = f"Provide feedback for {writing_type}. "
        focus_instruction = f"Focus on the following aspects: {', '.join(feedback_focus)}. "
        ai_messages = [
            {"role": "system", "content": custom_instructions + type_instruction + focus_instruction},
            {"role": "system", "content": "Provide constructive feedback, explain your suggestions, and offer specific examples for improvement."},
        ] + st.session_state.messages

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for chunk in stream_response(ai_messages, model):
                if chunk:
                    if model.startswith("gpt-"):
                        full_response += chunk.choices[0].delta.content or ""
                    else:
                        full_response += chunk['message']['content']
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.05)
            message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

        _, prompt_tokens, completion_tokens = get_ai_response(ai_messages, model)
        st.session_state.token_count["prompt"] += prompt_tokens
        st.session_state.token_count["completion"] += completion_tokens

    st.sidebar.subheader("Token Usage")
    st.sidebar.write(f"Prompt tokens: {st.session_state.token_count['prompt']}")
    st.sidebar.write(f"Completion tokens: {st.session_state.token_count['completion']}")
    st.sidebar.write(f"Total tokens: {sum(st.session_state.token_count.values())}")

if __name__ == "__main__":
    main()
