import streamlit as st
def app():
    st.title("Resume Analysis and Skills Advisor")

    st.write("""
    

    This project is an ATS (Applicant Tracking System) Scanner Tool built using Python and the Streamlit library for creating web applications. The tool allows users to upload their resumes (in PDF format) and perform two main operations:

    1. **Check ATS Score**: The tool assesses the compatibility between the user's resume and a selected job description. It utilizes a language model to analyze the resume text and the job description, identify relevant skills and keywords, and provide a percentage score indicating how well the resume matches the job requirements.

    2. **Check Missing Skills**: In this mode, the tool compares the user's resume with the selected job description and generates a list of essential skills or keywords that are missing from the resume.

    The tool is designed to be user-friendly, with a web-based interface where users can log in, select the desired operation, upload their resumes, and view the results.

    ## Code Explanation""")

    st.image('resume analyis.jpg', use_column_width=True)

    st.write("""
    The code is structured into several functions, each serving a specific purpose:

    1. **`authenticate`**: This function handles user authentication by checking if the provided username and password match the predefined credentials (or credentials stored in a dictionary).

    2. **`store_user_data`**: This function stores the user's data (name, email, phone number, selected option, selected job, resume filename, score, and missing keywords) in a CSV file for future reference or analysis.

    3. **`pdf_to_text`**: This function converts a PDF file (user's resume) into plain text, which is then used for further processing.

    4. **`construct_resume_score_prompt`**: This function constructs the prompt for the language model, combining the resume text and the job description, to assess the resume's compatibility with the job.

    5. **`construct_skills_prompt`**: This function constructs the prompt for the language model to identify the missing skills or keywords in the resume based on the job description.

    6. **`get_result`**: This function utilizes a generative model (in this case, the Google Generative AI library) to process the prompts and generate the desired output (resume score or missing skills).

    7. **`get_gemini_pro`**: This function initializes and configures the Google Generative AI model (Gemini-Pro) for use in the application.

    The main part of the code sets up the Streamlit app interface, handles user authentication, and provides the functionality for selecting the desired operation, uploading resumes, and displaying the results.

    """)
