import json
import ollama
from prompts import MATCH_SYSTEM_PROMPT
from schemas import (MatchResumetoJob,
                     SkillGapActionPlan)
from pydantic import ValidationError


# Extract only json part model's message
def extract_json(content: str) -> str:
    content = content.strip()

    start = content.find("{")
    end = content.rfind("}") + 1

    if start == -1 or end == 0:
        raise ValueError("No JSON object found in model response.")

    return content[start:end]

# Clear hyphen "-" if model returning hyphen
def clean_list_items(items: list[str]) -> list[str]:
    return [
        item.lstrip("-• ").strip()
        for item in items
    ]


def match_resume_to_job(resume_text: str, job_description: str):
    try:
        response = ollama.chat(
            model="llama3.2:latest",
            messages=[
                {
                    "role": "system",
                    "content": MATCH_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"""
    You must compare the resume with the job description.

    Resume:
    <{resume_text}>

    Job Description:
    <{job_description}>

    Return ONLY raw JSON.

    Do not include:
    - explanations
    - markdown
    - bullet points outside JSON
    - text before JSON
    - text after JSON

    The first character must be {{ and the last character must be }}.

    Use this exact JSON structure:

    {{
    "match_score": 80,
    "matched_skills": [
        "example skill"
    ],
    "missing_skills": [
        "example missing skill"
    ],
    "suggestions": [
        "example suggestion"
    ]
    }}

    Replace all example values with analysis from the resume.
    match_score must be an integer from 0 to 100.
    Do not return 0 unless the resume has no relevant match.
    """     
                }
            ],
            options= {"temperature":0.1}
        )

        content = response["message"]["content"]
        
        print("=" * 50)
        print("RAW MODEL RESPONSE")
        print(content)
        print("=" * 50)

        content = extract_json(content)
        review_data = json.loads(content)
        review = MatchResumetoJob.model_validate(review_data)
        result = review.model_dump()

        result["matched_skills"] = clean_list_items(result["matched_skills"])
        result["missing_skills"] = clean_list_items(result["missing_skills"])
        result["suggestions"] = clean_list_items(result["suggestions"])

        return result
    
    except ValidationError as e:
        return {
        "match_score": 0,
        "matched_skills": [],
        "missing_skills": [],
        "suggestions": [f"Schema validation error: {e}"]
        }
    
    except json.JSONDecodeError as e:
        return {
        "match_score": 0,
        "matched_skills": [],
        "missing_skills": [],
        "suggestions": [f"JSON parsing error: {e}"]
        }

    except Exception as error:
        return {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "suggestions": [f"Unexpected error: {error}"]
        }
    

def generate_skill_gap_action_plan(
    resume_text: str,
    job_description: str,
    missing_skills: list[str]
):
    try:
        response = ollama.chat(
            model="llama3.2:latest",
            messages=[
                {
                    "role": "system",
                    "content": MATCH_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"""
You are helping a job seeker understand their skill gaps honestly.

Resume:
<{resume_text}>

Job Description:
<{job_description}>

Missing Skills:
<{missing_skills}>

For each missing skill, classify it as one of:
- "supported"
- "partially_supported"
- "not_supported"

Rules:
1. Use only information from the resume.
2. Do not invent skills, licences, languages, software, or achievements.
3. If the resume clearly supports the skill, status is "supported".
4. If the resume has related experience but does not name the skill directly, status is "partially_supported".
5. If the resume does not support the skill at all, status is "not_supported".
6. Write a reason why you clarify status as "supported", "partially_supported", or "not_supported"
7. Only write a suggested resume bullet if status is "supported" or "partially_supported".
8. If status is "not_supported", suggested_resume_bullet must be an empty string.
9. learning_action should tell the candidate what to learn or prove next. Prefer practical self-learning actions.
10. Do not start list items with hyphens, bullet symbols, or markdown.
11. Return ONLY valid JSON.
12. Under "missing_skills" key, list all missing_skills in <{missing_skills}> 

Return this exact JSON structure:

{{
  "contact": {{
    "name":"",
    "email":"",
    "phone":""
    }},
  "target_role": "",
  "missing_skills": [] 
  "actions": [
    {{
      "skill": "",
      "status": "",
      "reason": "",
      "suggested_resume_bullet": "",
      "learning_action": ""
    }}
  ]
}}
"""
                }
            ],
            options={"temperature": 0.1}
        )

        content = response["message"]["content"]

        print("=" * 50)
        print("RAW SKILL GAP ACTION PLAN RESPONSE")
        print(content)
        print("=" * 50)

        content = extract_json(content)
        data = json.loads(content)

        action_plan = SkillGapActionPlan.model_validate(data)

        return action_plan.model_dump()

    except json.JSONDecodeError as error:
        return {
            "contact": {
                "name":"",
                "email":"",
                "phone":""
                },
            "target_role": "",
            "missing_skills":[],
            "actions": [
                {
                    "skill": "",
                    "status": "error",
                    "reason": f"JSON parsing error: {error}",
                    "suggested_resume_bullet": "",
                    "learning_action": ""
                }
            ]
        }

    except ValidationError as error:
        return {
            "contact": {
                "name":"",
                "email":"",
                "phone":""
                },
            "target_role": "",
            "missing_skills":[],
            "actions": [
                {
                    "skill": "",
                    "status": "error",
                    "reason": f"Schema validation error: {error}",
                    "suggested_resume_bullet": "",
                    "learning_action": ""
                }
            ]
        }

    except Exception as error:
        return {
            "contact": {
                "name":"",
                "email":"",
                "phone":""
                },
            "target_role": "",
            "missing_skills":[],
            "actions": [
                {
                    "skill": "",
                    "status": "error",
                    "reason": f"Unexpected error: {error}",
                    "suggested_resume_bullet": "",
                    "learning_action": ""
                }
            ]
        }