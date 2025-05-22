from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

from langchain_core.prompts import (SystemMessagePromptTemplate, 
                                    HumanMessagePromptTemplate,
                                    ChatPromptTemplate)



from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

load_dotenv()
api_key=os.getenv("GROQ_API_KEY")

llm=ChatGroq(groq_api_key=api_key,model_name="Gemma2-9b-It")


system = SystemMessagePromptTemplate.from_template("""You are helpful AI assistant who answer user question based on the provided context.""")

prompt = """
            **Task:** Extract key information from the following resume text.

            **Resume Text:**
            {context}

            **Instructions:**
            Please extract the following information and format it in a clear structure:

            1. **Contact Information:**
            - Name:
            - Email:
            - Phone Number:
            - Website/Portfolio:

            2. **Education:**
            - Institution Name:
            - Degree:
            - Field of Study:
            - Graduation Dates:

            3. **Experience:**
            - Job Title:
            - Company Name:
            - Location:
            - Dates of Employment:
            - Responsibilities/Projects:

            4. **Projects:**
            - Project Title:
            - Description/Technologies Used:
            - Outcomes/Results:

            5. **Skills:**
            - Programming Languages:
            - Technologies/Tools:

            6. **Additional Information:** (if applicable)
            - Certifications:
            - Awards or Honors:
            - Professional Affiliations:
            - Languages:

            **Question:**
            {question}

            **Extracted Information:**
        """

prompt = HumanMessagePromptTemplate.from_template(prompt)

def ask_llm(context, question):
    messages = [system, prompt]
    template = ChatPromptTemplate(messages)

    qna_chain = template | llm | StrOutputParser()
    return qna_chain.invoke({'context': context, 'question': question})


def validate_json(data):
    json_prompt = """
            Please validate and correct the following JSON data:

            **Extracted Information:**
            {data}

            Provide only the corrected JSON, with no preamble or explanation.

            **Corrected JSON:**"""

    json_prompt = HumanMessagePromptTemplate.from_template(json_prompt)
    json_messages = [system, json_prompt]
    json_template = ChatPromptTemplate(json_messages)

    json_chain = json_template | llm | JsonOutputParser()
    return json_chain.invoke({'data': data})
