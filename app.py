
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber

df = pd.read_csv("final_jobs.csv")
role_skill_freq = pd.read_csv("role_skill_freq.csv")

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.lower()

def extract_skills(text):
    keywords = [
        "python","sql","excel","machine learning","deep learning","nlp",
        "aws","azure","gcp","spark","hadoop","java","c++","javascript",
        "react","node","docker","kubernetes","sap","salesforce",
        "tableau","power bi","snowflake","pyspark",
        "recruitment","communication","management"
    ]
    return list(set([k for k in keywords if k in text]))

def recommend_skills(role, resume_skills):

    role_data = role_skill_freq[role_skill_freq['job_clean'] == role]
    role_data = role_data.sort_values(by='importance', ascending=False)

    top_skills = role_data['skills'].tolist()

    resume_skills = [s.lower() for s in resume_skills]

    matched = [s for s in top_skills if s.lower() in resume_skills]
    missing = [s for s in top_skills if s.lower() not in resume_skills]

    score = len(matched) / len(top_skills) if top_skills else 0

    return top_skills[:10], missing[:10], matched, score

def get_top_companies(role):
    return (
        df[df['job_clean'] == role]['company_name']
        .value_counts()
        .head(10)
    )



st.title("AI Skill Recommendation System")

# Upload resume
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf")

# Select role
roles = sorted(role_skill_freq['job_clean'].unique())
selected_role = st.selectbox("Select Job Role", roles)

if uploaded_file:

    # Extract resume text
    text = extract_text_from_pdf(uploaded_file)
    resume_skills = extract_skills(text)

    st.subheader("Extracted Skills from Resume")
    st.write(resume_skills if resume_skills else "No skills detected")

    # Analyze
    if st.button("Analyze"):

        top_skills, missing, matched, score = recommend_skills(
            selected_role, resume_skills
        )

        # Score
        st.subheader("Skill Match Score")
        st.progress(score)
        st.write(f"{round(score*100,2)}% match")

        # Skills
        st.subheader("Your Skills (Matched)")
        st.write(matched if matched else "No match")

        st.subheader("Missing Skills")
        st.write(missing if missing else "You are strong!")

        # Top Skills Chart
        st.subheader("Top Skills for Role")

        role_data = role_skill_freq[
            role_skill_freq['job_clean'] == selected_role
        ].sort_values(by='importance', ascending=False).head(10)

        fig, ax = plt.subplots()
        ax.barh(role_data['skills'], role_data['importance'])
        ax.invert_yaxis()
        st.pyplot(fig)

        # Companies Chart
        st.subheader("Top Hiring Companies")

        companies = get_top_companies(selected_role)

        fig2, ax2 = plt.subplots()
        ax2.barh(companies.index, companies.values)
        ax2.invert_yaxis()
        st.pyplot(fig2)
