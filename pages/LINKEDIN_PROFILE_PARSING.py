import streamlit as st
import time
import logging
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from bs4 import BeautifulSoup
import groq
import re

# Suppress selenium and Chrome WebDriver logging
logging.getLogger('selenium').setLevel(logging.ERROR)

# Check if required packages are installed
try:
    import lxml
    bs4_parser = "lxml"
except ImportError:
    bs4_parser = "html.parser"
    st.warning("""
    For better parsing results, install lxml:
    ```
    pip install lxml
    ```
    """)

# Debugging mode toggle
st.sidebar.title("SmartHire Setup")
debugging_mode = st.sidebar.checkbox("Enable Debugging Mode", value=True)




# Main title
st.title("SmartHire - LinkedIn Profile Analyzer")
st.subheader("AI-powered LinkedIn profile analysis for HR professionals")

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'profile_data' not in st.session_state:
    st.session_state.profile_data = None
if 'sections' not in st.session_state:
    st.session_state.sections = None
if 'current_section' not in st.session_state:
    st.session_state.current_section = None
if 'analysis' not in st.session_state:
    st.session_state.analysis = {}
if 'linkedin_email' not in st.session_state:
    st.session_state.linkedin_email = None
if 'linkedin_password' not in st.session_state:
    st.session_state.linkedin_password = None
if 'groq_api_key' not in st.session_state:
    st.session_state.groq_api_key = None

# Function to clean text - removes duplicates and extra whitespace
def clean_text(text):
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Check for section name duplications (common LinkedIn issue)
    # This handles cases like "HighlightsHighlights" or "ExperienceExperience"
    common_sections = [
        "Highlights", "Experience", "Education", "Skills", "About", "Activity",
        "Interests", "Licenses", "Certifications", "Open to work", "People you may know",
        "You might like", "More profiles for you", "Explore Premium profiles",
        "Licenses & certifications"
    ]
    
    for section in common_sections:
        pattern = f"({section})\\1+"  # Match section name repeated
        text = re.sub(pattern, r'\1', text, flags=re.IGNORECASE)
    
    # Check for repeated words or phrases
    words = text.split()
    cleaned_words = []
    
    i = 0
    while i < len(words):
        word = words[i]
        cleaned_words.append(word)
        
        # Skip any immediate duplicates
        while i + 1 < len(words) and words[i + 1] == word:
            i += 1
        
        i += 1
    
    return ' '.join(cleaned_words)

# Function to extract clean text from a BeautifulSoup element
def extract_clean_text(element):
    # Get raw text
    raw_text = element.get_text(strip=True, separator=' ')
    # Clean up the text
    return clean_text(raw_text)

# Function to scrape LinkedIn profile with Selenium and BeautifulSoup
def scrape_linkedin_profile(email, password, profile_url):
    # Debug container to show status/progress
    debug_container = st.empty()
    debug_container.info("Setting up Chrome driver...")
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--log-level=3")  # Minimal logging
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
    
    try:
        # Try using webdriver-manager for Chrome
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service as ChromeService
            debug_container.info("Installing Chrome driver...")
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            debug_container.warning(f"Using default Chrome WebDriver. If you encounter issues, install webdriver-manager: {str(e)}")
            # Fall back to direct Chrome driver
            driver = webdriver.Chrome(options=chrome_options)
        
        debug_container.info("Opening LinkedIn login page...")
        # Go to LinkedIn login page
        driver.get("https://www.linkedin.com/login")
        time.sleep(3)  # Wait for page to load
        
        debug_container.info("Entering login credentials...")
        # Check if on login page
        if "login" not in driver.current_url.lower():
            debug_container.error("Not on LinkedIn login page. Current URL: " + driver.current_url)
            return None, None
        
        # Find and fill in email and password fields
        try:
            email_field = driver.find_element(By.ID, "username")
            email_field.clear()
            email_field.send_keys(email)
            
            password_field = driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login button
            debug_container.info("Clicking login button...")
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            debug_container.info("Waiting for login to complete...")
            time.sleep(5)
            
            # Check if we're still on the login page (failed login)
            if "login" in driver.current_url.lower():
                error_element = driver.find_elements(By.ID, "error-for-username")
                if error_element:
                    debug_container.error(f"Login failed: {error_element[0].text}")
                else:
                    debug_container.error("Login failed: Still on login page")
                return None, None
                
            debug_container.info("Login successful. Navigating to profile...")
            
            # Now navigate to the profile URL
            driver.get(profile_url)
            debug_container.info("Waiting for profile to load...")
            time.sleep(5)
            
            # Check if we have access to the profile
            if "authwall" in driver.current_url.lower():
                debug_container.error("Access blocked: LinkedIn is requiring authentication")
                return None, None
            
            # Scroll down to load dynamic content
            debug_container.info("Scrolling to load profile content...")
            for i in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            
            # Get page source and parse with BeautifulSoup
            debug_container.info("Extracting profile data...")
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, bs4_parser)
            
            # Save the HTML for debugging
            if debugging_mode:
                with open("linkedin_profile.html", "w", encoding="utf-8") as f:
                    f.write(page_source)
            
            # Find the main profile section
            profile = soup.find('main', {'class': 'ntZHYFHDcSquahgjxCbZqrlcNXPHAoZMHVnYWM'})
            if not profile:
                debug_container.error("Could not find main profile section")
                # Try alternative structure
                profile = soup.find('div', {'class': 'ntZHYFHDcSquahgjxCbZqrlcNXPHAoZMHVnYWM'}) 
                if not profile:
                    profile = soup  # Use the entire page as fallback
                
            # Extract all sections with class 'artdeco-card'
            sections = profile.find_all('section', {'class': 'artdeco-card'})
            if not sections:
                debug_container.warning("No sections with 'artdeco-card' class found. Trying alternative approach...")
                # Try to get sections by other means
                sections = profile.find_all('section')
            
            if not sections:
                debug_container.error("Could not find any profile sections")
                return None, None
                
            debug_container.info(f"Found {len(sections)} profile sections")
            
            section_data = {}
            section_titles = []
            
            # Process each section
            for i, section in enumerate(sections):
                # Try to find section title
                title_elem = section.find(['h2', 'h3'])
                if title_elem:
                    # Get the title and clean any potential duplications
                    raw_title = title_elem.get_text(strip=True)
                    
                    # Fix common section title duplications like "HighlightsHighlights"
                    common_sections = [
                        "Highlights", "Experience", "Education", "Skills", "About", "Activity",
                        "Interests", "Licenses", "Certifications", "Open to work", "People you may know",
                        "You might like", "More profiles for you", "Explore Premium profiles",
                        "Licenses & certifications"
                    ]
                    
                    # Check if the title contains a duplication
                    title = raw_title
                    for section_name in common_sections:
                        if raw_title.lower() == (section_name.lower() + section_name.lower()):
                            title = section_name
                            break
                else:
                    title = f"Section {i+1}"
                
                # Make sure title is unique
                base_title = title
                counter = 1
                while title in section_titles:
                    title = f"{base_title} {counter}"
                    counter += 1
                
                # Store the section content with clean text
                section_data[title] = extract_clean_text(section)
                section_titles.append(title)
            
            debug_container.success(f"Successfully extracted {len(section_titles)} profile sections")
            return section_data, section_titles
            
        except NoSuchElementException as e:
            debug_container.error(f"Element not found: {str(e)}")
            return None, None
        except ElementNotInteractableException as e:
            debug_container.error(f"Element not interactable: {str(e)}")
            return None, None
        except Exception as e:
            debug_container.error(f"Error during login: {str(e)}")
            return None, None
            
    except Exception as e:
        debug_container.error(f"Error occurred: {str(e)}")
        return None, None
    finally:
        try:
            driver.quit()
            debug_container.info("Chrome driver closed")
        except:
            pass

# Function to analyze profile section with Groq
def analyze_with_groq(section_name, section_content, api_key):
    try:
        client = groq.Client(api_key=api_key)
        
        prompt = f"""
        You are an expert HR assistant. Analyze the following LinkedIn profile section "{section_name}" and provide valuable insights for HR professionals:
        
        {section_content}
        
        Your analysis should include:
        1. Key skills and qualifications
        2. Relevant experience
        3. Potential fit for roles
        4. Any red flags or points of concern
        5. Suggestions for interview questions
        
        Format your response in a clear, structured way.
        """
        
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # Use an appropriate Groq model
            messages=[
                {"role": "system", "content": "You are an expert HR assistant analyzing LinkedIn profiles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing section: {str(e)}"

# Login section (only shown if not logged in)
if not st.session_state.logged_in:
    with st.container():
        st.subheader("LinkedIn Login")
        st.warning("⚠️ Note: Your credentials are used only for authentication with LinkedIn and are not stored.")
        
        with st.form("login_form"):
            linkedin_email = st.text_input("LinkedIn Email", type="default")
            linkedin_password = st.text_input("LinkedIn Password", type="password")
            groq_api_key = st.text_input("Groq API Key", type="password")
            
            login_submitted = st.form_submit_button("Login")
            
            if login_submitted:
                if not linkedin_email or not linkedin_password or not groq_api_key:
                    st.error("Please fill in all fields")
                else:
                    # Store credentials in session state
                    st.session_state.linkedin_email = linkedin_email
                    st.session_state.linkedin_password = linkedin_password
                    st.session_state.groq_api_key = groq_api_key
                    
                    # Set logged in state to true
                    st.session_state.logged_in = True
                    st.success("Login credentials saved")
                    st.rerun()

# Profile URL input and scraping (only shown if logged in)
if st.session_state.logged_in:
    with st.container():
        st.subheader("Profile Analysis")
        
        # Profile URL input
        with st.form("profile_form"):
            profile_url = st.text_input("Enter LinkedIn Profile URL")
            scrape_submitted = st.form_submit_button("Analyze Profile")
            
            if scrape_submitted:
                if not profile_url:
                    st.error("Please enter a profile URL")
                else:
                    # Show loading spinner
                    with st.spinner("Scraping LinkedIn profile... This may take a minute."):
                        # Scrape LinkedIn profile
                        section_data, section_titles = scrape_linkedin_profile(
                            st.session_state.linkedin_email, 
                            st.session_state.linkedin_password, 
                            profile_url
                        )
                        
                        if section_data and section_titles:
                            st.session_state.profile_data = section_data
                            st.session_state.sections = section_titles
                            st.success("Profile scraped successfully!")
                            
                            # If debugging is enabled, show raw data
                            if debugging_mode:
                                with st.expander("Debug: Raw Profile Data"):
                                    st.json(section_data)
                            
                            st.rerun()
                        else:
                            st.error("Failed to scrape profile. Please check the URL and your login credentials.")
                            
                            # Suggest manual login first
                            st.warning("""
                            LinkedIn sometimes blocks automated logins. Try these steps:
                            1. Login to LinkedIn manually in your browser first
                            2. Make sure you're using the correct email/password
                            3. Check if the profile URL is correct and accessible
                            """)
                            
                            # Offer direct profile URL input
                            st.info("As an alternative, you can copy-paste the profile content directly")
                            manually_pasted = st.text_area("Paste LinkedIn profile content here (if scraping fails)", height=200)
                            
                            if manually_pasted and st.button("Process pasted content"):
                                try:
                                    # Process the manually pasted content
                                    soup = BeautifulSoup(manually_pasted, bs4_parser)
                                    
                                    # Process the pasted content and check for section headers
                                    # Try to identify sections in the pasted content
                                    sections_data = {}
                                    
                                    # Look for potential section headers in the raw text
                                    common_sections = [
                                        "Highlights", "Experience", "Education", "Skills", "About", "Activity",
                                        "Interests", "Licenses & certifications"
                                    ]
                                    
                                    # First, try to split by known section headers
                                    found_sections = False
                                    raw_text = soup.get_text(separator=' ', strip=True)
                                    
                                    for section_name in common_sections:
                                        # Check for the section name (with duplications)
                                        pattern = f"({section_name}|{section_name}{section_name})"
                                        if re.search(pattern, raw_text, re.IGNORECASE):
                                            found_sections = True
                                            clean_section_name = section_name
                                            # Extract this section's content and clean it
                                            section_text = clean_text(raw_text)
                                            sections_data[clean_section_name] = section_text
                                    
                                    # If no sections were identified, just use the whole text as "Profile"
                                    if not found_sections:
                                        sections_data["Profile"] = clean_text(raw_text)
                                    
                                    # Get the section titles
                                    sections_titles = list(sections_data.keys())
                                    
                                    
                                    st.session_state.profile_data = sections_data
                                    st.session_state.sections = sections_titles
                                    st.success("Content processed successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error processing content: {e}")
        
        # Display profile sections if available
        
        if st.session_state.sections:
            st.subheader("Profile Sections")
            
            # Create columns for section buttons
            cols = st.columns(3)
            
            # Display section buttons
            for i, section_name in enumerate(st.session_state.sections):
                col_idx = i % 3
                if cols[col_idx].button(section_name, key=f"section_{i}"):
                    st.session_state.current_section = section_name
                    
                    # Check if analysis already exists for this section
                    if section_name not in st.session_state.analysis:
                        # Show loading spinner
                        with st.spinner(f"Analyzing {section_name} section..."):
                            # Get section content
                            section_content = st.session_state.profile_data[section_name]
                            
                            # Analyze with Groq
                            analysis = analyze_with_groq(
                                section_name, 
                                section_content, 
                                st.session_state.groq_api_key
                            )
                            
                            # Store analysis
                            st.session_state.analysis[section_name] = analysis
                    
                    st.rerun()
            
            # Display selected section analysis
            if st.session_state.current_section:
                st.subheader(f"Analysis of {st.session_state.current_section}")
                
                # Display the raw section content in an expander
                with st.expander("Raw Section Content"):
                    st.text(st.session_state.profile_data[st.session_state.current_section])
                
                # Display the analysis
                st.markdown(st.session_state.analysis.get(st.session_state.current_section, "Analysis not available"))
                
                # Option to copy analysis to clipboard
                st.text_area("Copy analysis", 
                             st.session_state.analysis.get(st.session_state.current_section, ""), 
                             height=100)

# Footer
st.markdown("---")
st.caption("SmartHire - LinkedIn Profile Analyzer | Powered by Groq AI")