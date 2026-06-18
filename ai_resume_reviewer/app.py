import streamlit as st
from resume_parser import extract_text_from_pdf
from llm_client import (match_resume_to_job,
                           generate_skill_gap_action_plan)
from io import StringIO

st.title("AI Resume Job Matcher v1")
st.write("Upload your resume, paste a job description, and get tailored job-match feedback.")

# Initialise session state near the top of app.py
if "job_match_result" not in st.session_state:
    st.session_state.job_match_result = None

if "skill_gap_action_plan" not in st.session_state:
    st.session_state.skill_gap_action_plan = None


def display_job_match(review: dict):
    st.subheader("Match Score")
    st.metric("Match Score", f"{review['match_score']}/100")

    st.subheader("Matched Skills")
    for item in review["matched_skills"]:
        st.write("-", item)

    st.subheader("Missing Skills")
    for item in review["missing_skills"]:
        st.write("-", item)

    st.subheader("Suggestions")
    for item in review["suggestions"]:
        st.write("-", item)


def build_job_match_report(review: dict) -> str:
    report = f"""
Resume Job Match Report

Match Score
{review["match_score"]}/100

Matched Skills
{chr(10).join("- " + item for item in review["matched_skills"])}

Missing Skills
{chr(10).join("- " + item for item in review["missing_skills"])}

Suggestions
{chr(10).join("- " + item for item in review["suggestions"])}
"""
    return report.strip()


def build_action_plan_report(action_plan: dict) -> str:
    
    report = StringIO()
    report.write(f"""
Skill Gap Action Plan

Candidate Contact
Name: {action_plan["contact"]["name"]}
Email: {action_plan["contact"]["email"]}
Phone number: {action_plan["contact"]["phone"]}

Missing Skills
{", ".join(skill for skill in action_plan["missing_skills"])}

""")

    for index, action in enumerate(action_plan["actions"], start=1):
        skill = action["skill"].title()
        status = action["status"].replace("_", " ").title()
        reason = action["reason"]
        resume_bullet = action.get("suggested_resume_bullet")
        learning_action = action.get("learning_action")

        # Write each line to the in-memory buffer
        report.write(f"{index}. {skill}\n")
        report.write(f"Status: {status}\n")
        report.write(f"Reason: {reason}\n")

        if resume_bullet:
            report.write("Suggested Resume Bullet:\n")
            report.write(f"- {resume_bullet}\n")

        if learning_action:
            report.write("Learning Action:\n")
            report.write(f"- {learning_action}\n")

    drafted_text = report.getvalue().strip()
    report.close()
    return drafted_text


def display_skill_gap_action_plan(action_plan: dict):
    st.subheader("Skill Gap Action Plan")

    st.subheader("Target Role")
    
    st.write(action_plan["target_role"])
    
    st.markdown(f"### Missing Skills")
    m = ", ".join(skill for skill in action_plan["missing_skills"])
    st.write(m)

    st.markdown(f'### Suggested Action Plan')
    for index, action in enumerate(action_plan["actions"], start=1):
        st.markdown(f"#### {index}. {action['skill'].title()}")

        st.write("Status:", action["status"].replace("_", " ").title())
        st.write("Reason:", action["reason"])

        if action["suggested_resume_bullet"]:
            st.write("Suggested Resume Bullet:")
            st.write("-", action["suggested_resume_bullet"])

        st.write("Learning Action:")
        st.write("-", action["learning_action"]) 


# Input job description
job_description = st.text_area(
    "Paste the job description here",
    height=250,
    placeholder="Paste the full job description here..."
)
if st.session_state.get("previous_job_description") != job_description:
    st.session_state.previous_job_description = job_description
    st.session_state.job_match_result = None
    st.session_state.skill_gap_action_plan = None

debug_mode = st.checkbox("Show debug info")

uploaded_file = st.file_uploader(
    "Upload your resume PDF here",
    type=["pdf"]
)


if uploaded_file is not None:
    st.success("PDF uploaded successfully")
    resume_text = extract_text_from_pdf(uploaded_file)

    current_file_name = uploaded_file.name

    if st.session_state.get("uploaded_file_name") != current_file_name:
        st.session_state.uploaded_file_name = current_file_name
        st.session_state.job_match_result = None
        st.session_state.skill_gap_action_plan = None

    st.subheader("Extracted Resume Text")
    with st.expander("View extracted resume text"):
        st.text_area(
            "Resume content",
            resume_text,
            height=300
        )
    
    
    if st.button("Match Resume to Job"):
        if not resume_text:
            st.error("Please upload a PDF resume first.")
        elif not job_description.strip():
            st.error("Please paste a job description first.")
        else:
            with st.spinner("Matching resume to job..."):
                st.session_state.job_match_result = match_resume_to_job(
                    resume_text,
                    job_description
                )

            # Reset old tailored suggestions and action plan when a new match is generated
            st.session_state.skill_gap_action_plan = None
            
    if st.session_state.job_match_result is not None:
        review = st.session_state.job_match_result
        
        if debug_mode:
            st.write(type(review))
            st.subheader("Debug: Parsed AI Output")
            st.write(review)

        if isinstance(review, dict):
            display_job_match(review)
            report_text = build_job_match_report(review)

            st.download_button(
                label="Download Job Match Report",
                data=report_text,
                file_name="job_match_report.txt",
                mime="text/plain"
            )


            if st.button("Generate Skill Gap Action Plan"):
                with st.spinner("Generating skill gap action plan..."):
                    st.session_state.skill_gap_action_plan = generate_skill_gap_action_plan(
                        resume_text,
                        job_description,
                        review["missing_skills"]
                    )
        else:
            st.error(review)


    if st.session_state.skill_gap_action_plan is not None:
        action_plan = st.session_state.skill_gap_action_plan

        if debug_mode:
            st.write(type(action_plan))
            st.subheader("Debug: Skill Gap Action Plan Output")
            st.write(action_plan)

        display_skill_gap_action_plan(action_plan)
        report_text = build_action_plan_report(action_plan)

        st.download_button(
            label="Download Skill Gap Action Plan Report",
            data=report_text,
            file_name="skill_gap_action_plan.txt",
            mime="text/plain"
        )
        