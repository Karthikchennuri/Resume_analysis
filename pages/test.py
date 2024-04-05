import os
import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import csv
from datetime import datetime, timedelta
import shutil


# Import generativeai library only if it's available
try:
    import google.generativeai as genai
except ImportError:
    genai = None

load_dotenv()

# Define the path to the CSV file
csv_file_path = 'user_data2.csv'

# Define the path to save uploaded resumes
upload_directory = 'uploaded_resumes'  # New directory for uploaded resumes

# Function to authenticate user
def authenticate(username, password):
    # Define a dictionary of valid usernames and passwords
    valid_credentials = {
        "user1": "neeraj",
        "user2": "password2",
        "user3": "password3",
        # Add more usernames and passwords as needed
    }
 # Check if the provided username exists and if the corresponding password matches
    if username in valid_credentials and valid_credentials[username] == password:
        return True
    else:
        return False
# Function to store user data in CSV file
def store_user_data(name, email, phone, selected_option, selected_job, filename=None, score=None, missing_keywords=None):
    try:
        current_time = datetime.now()

        # Initialize the data dictionary
        data = {
            'Name': name,
            'Email': email,
            'Phone': phone,
            'Selected Option': selected_option,
            'Selected Job': selected_job,
            'Filename': filename,
            'Score': score if selected_option == "Check ATS Score" else "",
            'Missing Keywords': missing_keywords if selected_option == "Check Missing Skills" else "",
            'Timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # Write data to CSV file
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            writer.writerow(data)

    except Exception as e:
        st.error(f"An error occurred while storing the user data: {e}")

# Function to convert PDF to text
def pdf_to_text(pdf_file):
    reader = PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += str(page.extract_text())
    return text

# Function to construct prompt for resume score assessment
def construct_resume_score_prompt(resume, job_description):
    resume_score_prompt = f'''Act as a HR Manager with 20 years of experience.
    Compare the resume provided below with the job description given below.
    Check for key skills in the resume that are related to the job description.
    Rate the resume out of 100 based on the matching skill set.
    Assess the score with high accuracy.
    Here is the Resume text: {resume}
    Here is the Job Description: {job_description}

    I want the response as a single string in the following structure score:%'''
    return resume_score_prompt

# Function to construct prompt for missing skills identification
def construct_skills_prompt(resume, job_description):
    skill_prompt = f'''Act as a HR Manager with 20 years of experience.
    Compare the resume provided below with the job description given below.
    Check for key skills in the resume that are related to the job description.
    List the missing key skillset from the resume.
    I just need the extracted missing skillset.
    Here is the Resume text: {resume}
    Here is the Job Description: {job_description}

    I want the response as a list of missing skill word'''
    return skill_prompt

# Function to get result from generative model
def get_result(input):
    model = get_gemini_pro()
    if model:
        response = model.generate_content(input)
        return response.text
    else:
        return None

# Function to initialize generative model
def get_gemini_pro():
    if genai:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        return genai.GenerativeModel('gemini-pro')
    else:
        st.error("Could not import generativeai library. Please make sure it's installed.")

def app():
    st.title("Resume Analysis")

    # Authentication
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    if authenticate(username, password):
        st.sidebar.success("Logged in ")
        #st.title('ATS Tracker Tool')

        name = st.text_input('Enter Your Name')
        email = st.text_input('Enter Your Email')
        phone = st.text_input('Enter Your Phone Number')

        job_descriptions = {
            'Software Engineer at Meta': 'Innovate and collaborate on the development of cutting-edge software solutions at Meta. Utilize your expertise in programming languages such as Java, Python, and C++ to design and implement scalable and efficient software applications. Leverage modern development methodologies and tools to drive the delivery of high-quality software products. Skills required: Java, Python, C++, Software Development, Agile Methodologies, Problem-Solving.',
            'Data Scientist at Walmart': 'Join the data-driven team at Walmart as a Data Scientist and leverage your analytical skills to extract insights from vast and complex datasets. Apply statistical analysis and machine learning techniques to solve business challenges and drive data-informed decision-making. Collaborate with cross-functional teams to develop and deploy data-driven solutions that optimize processes and drive business growth. Skills required: Data Analysis, Machine Learning, Statistical Analysis, Python, R, SQL.',
            'DevOps Engineer at Amazon': 'Join the innovative DevOps team at Amazon and lead the design and implementation of robust and scalable DevOps solutions. Utilize your expertise in cloud technologies such as AWS and Azure to automate infrastructure provisioning, configuration management, and deployment processes. Collaborate with software development teams to streamline CI/CD pipelines and ensure seamless delivery of software products. Skills required: DevOps, AWS, Azure, CI/CD, Infrastructure Automation.',
            'Python Developer at TCS': 'oin the dynamic team at TCS as a Python Developer and contribute to the development and maintenance of Python-based applications. Utilize your proficiency in Python programming and web development frameworks such as Django and Flask to create scalable and secure software solutions. Collaborate with cross-functional teams to understand requirements and deliver high-quality software products. Skills required: Python, Django, Flask, Web Development, Software Development.',
            'Data Engineer at Google': 'Join the innovative data engineering team at Google and drive the design and implementation of scalable data pipelines and infrastructure. Utilize your expertise in big data technologies such as Hadoop, Spark, and Kafka to process and analyze large volumes of data. Collaborate with data scientists and analysts to build robust data platforms that enable data-driven decision-making and insights. Skills required: Big Data, Hadoop, Spark, Kafka, Data Processing.'
            # Add more job descriptions as needed
        }

        selected_option = st.radio("Select Option", ["Check ATS Score", "Check Missing Skills"])

        # Get the current session state
        session_state = st.session_state

        if selected_option == "Check ATS Score":
            selected_job = st.selectbox('Select Job Description', list(job_descriptions.keys()))

            uploaded_file = st.file_uploader('Upload Your Resume', type=['pdf'])

            if st.button('Get Score'):
                if uploaded_file is None:
                    st.error('Upload your Resume')
                else:
                    try:
                        resume = pdf_to_text(uploaded_file)

                        # Save uploaded resume
                        if not os.path.exists(upload_directory):
                            os.makedirs(upload_directory)

                        # Generate unique filename for each uploaded PDF
                        resume_filename = f"{name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
                        resume_path = os.path.join(upload_directory, resume_filename)
                        with open(resume_path, 'wb') as f:
                            f.write(uploaded_file.getvalue())

                        job_description = job_descriptions.get(selected_job, '')
                        if job_description:
                            score_prompt = construct_resume_score_prompt(resume, job_description)
                            result = get_result(score_prompt)
                            if result:
                                final_result = result.split(":")[1]
                                if '%' not in final_result:
                                    final_result = final_result + '%'
                                result_str = f"""
                                <style>
                                p.a {{
                                  font: bold 25px Arial;
                                }}
                                </style>
                                <p class="a">Your Resume matches {final_result} with the Job Description</p>
                                """
                                st.markdown(result_str, unsafe_allow_html=True)

                                # Store user data in CSV file
                                store_user_data(name, email, phone, selected_option, selected_job, resume_filename, final_result)
                    except Exception as e:
                        print(f'{type(e).__name__}: {e}')

        elif selected_option == "Check Missing Skills":
            selected_job = st.selectbox('Select Job Description', list(job_descriptions.keys()))

            uploaded_file = st.file_uploader('Upload Your Resume', type=['pdf'])

            if st.button('Check Missing Skills'):
                if uploaded_file is None:
                    st.error('Upload your Resume')
                else:
                    try:
                        resume = pdf_to_text(uploaded_file)

                        # Save uploaded resume
                        if not os.path.exists(upload_directory):
                            os.makedirs(upload_directory)

                        # Generate unique filename for each uploaded PDF
                        resume_filename = f"{name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
                        resume_path = os.path.join(upload_directory, resume_filename)
                        with open(resume_path, 'wb') as f:
                            f.write(uploaded_file.getvalue())

                        job_description = job_descriptions.get(selected_job, '')
                        if job_description:
                            skill_prompt = construct_skills_prompt(resume, job_description)
                            result = get_result(skill_prompt)
                            if result:
                                st.write('Your Resume misses the following keywords:')
                                st.write(result)

                                # Store user data in CSV file
                                store_user_data(name, email, phone, selected_option, selected_job, resume_filename, missing_keywords=result)
                    except Exception as e:
                        print(f'{type(e).__name__}: {e}')
    else:
        if login_button:
            st.sidebar.error("Authentication failed. Invalid username or password")
