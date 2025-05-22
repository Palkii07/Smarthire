import streamlit as st
from PIL import Image
import time

# Set page config
st.set_page_config(
    page_title="SmartHire",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        # "HR PORTAL": "https://www.example.com",
        # "Linkedin": "https://www.linkedin.com/in/",
        # "Naukri": "https://www.naukri.com/",
        # "GitHub": "https://www.github.com/",
        "Get Help": "mailto:sachdevapalki@gmail.com"

    })

# Custom CSS for dark mode and animations
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            background-color: #1f1f2e;
            color: #f5f6fa;
        }

        .block-container {
            padding-top: 2rem;
        }

        h1, h4 {
            text-align: center;
            color: #f1c40f;
        }

        .highlight-card {
            background-color: #2d2d44;
            padding: 1.2rem;
            border-radius: 12px;
            margin: 10px 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        }

        .stTextInput>div>div>input {
            background-color: #2c3e50;
            color: white;
            border: 1px solid #f1c40f;
            border-radius: 8px;
            padding: 10px;
        }

        .stButton button {
            background-color: #f1c40f;
            color: black;
            font-weight: bold;
            border-radius: 10px;
            transition: all 0.3s ease-in-out;
        }

        .stButton button:hover {
            transform: scale(1.05);
            background-color: #f39c12;
        }

        .fade-in {
            animation: fadeIn 1.5s ease-in;
        }

        @keyframes fadeIn {
            from {opacity: 0;}
            to {opacity: 1;}
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='fade-in'>🚀 SmartHire</h1>", unsafe_allow_html=True)
st.markdown("<h4 class='fade-in'>Your AI-Powered Recruitment Assistant</h4>", unsafe_allow_html=True)
st.markdown("---")

# Animated Welcome Input
name = st.text_input("👤 What's your name?", placeholder="Enter your name here")
user_id = st.number_input("👤 What's your ID?", min_value=0, step=1, format="%d")
user_id = int(user_id)  # Ensure it's an in


if name and user_id:
    st.success(f"✨ Welcome aboard, **{name}**! Use the sidebar to explore SmartHire's powerful features.")
    st.balloons()
    time.sleep(1.2)

    # Feature Highlights
    st.markdown("### 🔍 Key Features")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="highlight-card">
        <h4>📄 Resume Analysis</h4>
        <p>Get instant ATS-friendly resume scores, keyword suggestions, and red flags.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="highlight-card">
        <h4>🔗 LinkedIn Insights</h4>
        <p>Analyze candidates' LinkedIn profiles with smart summarization and skill extraction.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="highlight-card">
        <h4>🤖 JD Matching</h4>
        <p>Match job descriptions with resumes to assess the best-fit candidates.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="highlight-card">
        <h4>💬 Smart Q&A</h4>
        <p>Ask questions about uploaded documents using AI — fast, accurate, and interactive.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("✅ Ready to get started? Use the **sidebar** to explore the tools.")

else:
    st.info("👋 Enter your name to begin your SmartHire journey!")

