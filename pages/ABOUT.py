import streamlit as st
from pymongo import MongoClient
import re
from dotenv import load_dotenv
import os
load_dotenv()
Mongo_uri=os.getenv("MONGO_URI")
# MongoDB connection details — replace with your actual username and password
MONGO_URI = Mongo_uri
DB_NAME = "smarthire"
COLLECTION_NAME = "subscribers"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

# Page config and styling
st.set_page_config(page_title="About SmartHire", page_icon="🧠", layout="centered")

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
            max-width: 700px;
        }

        h1 {
            text-align: center;
            color: #f1c40f;
            font-weight: 700;
        }

        h4 {
            text-align: center;
            color: #cccccc;
            font-weight: 400;
            margin-bottom: 2rem;
        }

        p {
            text-align: center;
            font-size: 1.1em;
            color: #dddddd;
            line-height: 1.6;
        }

        .subscribe-box {
            background-color: #2d2d44;
            padding: 20px;
            border-radius: 15px;
            margin-top: 2rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        }

        input[type="email"] {
            background-color: #2c3e50;
            color: white;
            border: 2px solid #f1c40f;
            border-radius: 8px;
            padding: 12px;
            width: 100%;
            font-size: 1em;
            margin-bottom: 1rem;
            box-sizing: border-box;
        }

        button {
            background-color: #f1c40f;
            color: black;
            font-weight: 700;
            padding: 12px 20px;
            width: 100%;
            border-radius: 12px;
            cursor: pointer;
            transition: background-color 0.3s ease-in-out;
            border: none;
        }

        button:hover {
            background-color: #d4ac0d;
        }

        .footer {
            text-align: center;
            color: #888;
            margin-top: 3rem;
            font-size: 0.9em;
        }
    </style>
""", unsafe_allow_html=True)

# Title and subtitle
st.markdown("<h1>SmartHire 🧠</h1>", unsafe_allow_html=True)
st.markdown("<h4>AI-powered Resume Insights & Career Tools</h4>", unsafe_allow_html=True)

# Logo image centered
logo_path = "assets/Logo.png"
cols = st.columns([1, 2, 1])
with cols[1]:
    st.image(logo_path, use_container_width=True)

# Intro paragraph
st.markdown("""
<p>
Welcome to <strong>SmartHire</strong>, your AI-powered assistant designed to decode resumes,
evaluate ATS scores, extract LinkedIn insights, and answer your questions about candidate documents.
</p>
""", unsafe_allow_html=True)

# Newsletter subscription box
# st.markdown('<div class="subscribe-box">', unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center; color:#f1c40f;'>Subscribe to Our Newsletter 📬</h3>", unsafe_allow_html=True)
email = st.text_input("Enter your email to receive updates, tips, and exclusive AI hiring insights", "")

if st.button("Subscribe"):
    email = email.strip().lower()
    if not is_valid_email(email):
        st.error("⚠️ Please enter a valid email address.")
    else:
        existing = collection.find_one({"email": email})
        if existing:
            st.warning("⚠️ This email is already subscribed.")
        else:
            collection.insert_one({"email": email})
            st.success("🎉 Thank you for subscribing! You will hear from us soon.")

st.markdown('</div>', unsafe_allow_html=True)

# Bottom banner image
banner_path = "assets/Banner.jpg"
st.image(banner_path, use_container_width=True)

# Footer
st.markdown("<div class='footer'>Created with ❤️ by Palki</div>", unsafe_allow_html=True)
