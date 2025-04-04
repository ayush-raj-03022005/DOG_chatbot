import streamlit as st
import requests
import json
import time
import re

# Set up the page
st.set_page_config(
    page_title="Dog Training Assistant",
    page_icon="🐕",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("🐾 Professional Dog Training Assistant")

# API configuration###############################################
API_KEY = "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"
MODEL = "deepseek/deepseek-r1-zero:free"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm your Dog Training Assistant. Ask me anything about dog training and I'll provide structured step-by-step guidance!"
    }]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def get_ai_response():
    # Enhanced system prompt for structured responses
    prompt = {
        "model": MODEL,
        "messages": [{
            "role": "system",
            "content": """You are a professional dog trainer. Always respond with this exact structure:
            
            "To [achieve goal], follow these steps:
            
            STEP 1: [Clear heading]
            - Action 1
            - Action 2
            💡 Tip: [Relevant tip]
            
            STEP 2: [Clear heading]
            - Primary action
            - Secondary action
            ⚠️ Warning: [Important caution]
            
            ... (continue steps as needed)
            
            Final Tips:
            - [Summary tip 1]
            - [Summary tip 2]
            
            Remember: [Encouraging closing statement]"

            Rules:
            1. Use exactly 5-7 steps
            2. Each step has 2-3 actions
            3. Include 1 tip/warning per step
            4. Use simple emojis (💡, ⚠️)
            5. No markdown formatting
            6. Maintain previous context
            
            
            But you can also have normal conversation with the user"""
        }] + st.session_state.messages[-4:]  # Keep last 4 messages for context
    }

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            data=json.dumps(prompt),
            timeout=15
        )

        if response.status_code == 200:
            raw = response.json()["choices"][0]["message"]["content"]
            # Enhanced cleaning for consistent formatting
            cleaned = re.sub(r'(\*\*|`|\\boxed{)|(```\w*)|(-{3,})', '', raw)
            return cleaned.strip()
        return "Please ask about dog training techniques."

    except Exception as e:
        return f"Error: {str(e)}"

# Chat interface
if user_input := st.chat_input("Ask about dog training..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        response = get_ai_response()
        lines = response.split('\n')
        
        # Animated step-by-step display
        display_text = ""
        container = st.empty()
        
        for line in lines:
            display_text += line + "\n"
            container.markdown(display_text)
            time.sleep(0.2 if line.startswith("STEP") else 0.05)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
