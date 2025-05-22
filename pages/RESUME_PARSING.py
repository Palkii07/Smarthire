import streamlit as st
import pymupdf
import json

from scripts.llm import ask_llm, validate_json

st.title("Resume Parsing")
st.write("Upload a resume in PDF format to extract information")

uploaded_file = st.file_uploader("Choose a PDF resume file", type="pdf")

# Add a text area for required skills input
st.subheader("Required Skills")
required_skills = st.text_area(
    "Enter the required skills (one per line)",
    placeholder="Python\nSQL\nMachine Learning\nData Analysis"
)

if uploaded_file is not None:
    bytearray = uploaded_file.read()
    pdf = pymupdf.open(stream=bytearray, filetype="pdf")

    context = ""
    for page in pdf:
        context = context + "\n\n" + page.get_text()

    pdf.close()

    question = """You are tasked with parsing a job resume. Your goal is to extract relevant information in a valid structured 'JSON' format.
                Include these fields:
                - "personal_info" (name, email, phone, location)
                - "education" (array of educational qualifications with institution, degree, year)
                - "experience" (array of work experiences with company, position, duration, responsibilities)
                - "skills" (array of all technical and soft skills mentioned)
                - "certifications" (array of certifications if any)
                - "languages" (array of languages known if mentioned)
                
                Output only valid JSON without any preamble or explanations."""

    if st.button("Parse Resume"):
        with st.spinner("Parsing Resume..."):
            response = ask_llm(context=context, question=question)
        
        with st.spinner("Validating JSON..."):
            parsed_data = validate_json(response)
        
        # Display the parsed information
        st.subheader("Extracted Information")
        st.json(parsed_data)
        
        # Process skills matching if required skills are provided
        if required_skills:
            required_skills_list = [skill.strip() for skill in required_skills.split('\n') if skill.strip()]
            
            # Extract parsed skills from the response
            try:
                # If parsed_data is a string, try to parse it as JSON
                if isinstance(parsed_data, str):
                    parsed_data = json.loads(parsed_data)
                
                # Now parsed_data should be a dictionary
                candidate_skills = [skill.strip().lower() for skill in parsed_data.get("skills", [])]
                
                # Find missing skills
                missing_skills = []
                for skill in required_skills_list:
                    skill_lower = skill.lower()
                    found = False
                    for candidate_skill in candidate_skills:
                        if skill_lower in candidate_skill or candidate_skill in skill_lower:
                            found = True
                            break
                    if not found:
                        missing_skills.append(skill)
                
                # Calculate match percentage
                if required_skills_list:
                    match_percentage = ((len(required_skills_list) - len(missing_skills)) / len(required_skills_list)) * 100
                else:
                    match_percentage = 100
                
                # Display skills matching results
                st.subheader("Skills Match Analysis")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Match Percentage", f"{match_percentage:.1f}%")
                
                with col2:
                    st.metric("Missing Skills", len(missing_skills))
                
                if missing_skills:
                    st.write("**Missing Skills:**")
                    for skill in missing_skills:
                        st.write(f"- {skill}")
                else:
                    st.success("All required skills found!")
                
                # Show candidate skills
                st.write("**Candidate Skills:**")
                st.write(", ".join(parsed_data.get("skills", [])))
            
            except (json.JSONDecodeError, TypeError, AttributeError) as e:
                st.error(f"Could not analyze skills - Error: {str(e)}")
                st.write(parsed_data)
        
        st.write("You can copy the JSON output and use it in your application.")
        st.balloons()
else:
    st.info("Please upload a resume to begin parsing")