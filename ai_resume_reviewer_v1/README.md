# AI Resume Job Matcher v1

A Streamlit AI application that compares a resume PDF against a job description, generates a job match score, identifies missing skills, and creates an honest skill gap action plan using a local Ollama LLM.

This project was built as part of my Month 2 AI Engineering learning roadmap.

---

## Project Overview

Many job seekers do not know how well their resume matches a specific job description.

This app helps users:

1. Upload a resume PDF
2. Paste a job description
3. Get a resume-to-job match score
4. Identify matched and missing skills
5. Generate a practical skill gap action plan
6. Download reports as text files

The app focuses on honest resume improvement. It does not encourage users to fake experience, licences, software knowledge, languages, or achievements.

---

## Features

### Resume PDF Upload

Users can upload a PDF resume. The app extracts resume text using Python PDF processing.

### Job Description Input

Users paste the full job description into a text box.

### Resume-to-Job Matching

The app compares the resume against the job description and returns:

- Match score
- Matched skills
- Missing skills
- Suggestions

### Skill Gap Action Plan

For each missing skill, the app classifies it as:

- `supported`
- `partially_supported`
- `not_supported`

Each skill gap includes:

- Reason
- Suggested resume bullet, if honestly supported
- Learning action

### Download Reports

Users can download:

- Job match report
- Skill gap action plan report

### Debug Mode

Debug mode shows parsed AI outputs and helps inspect model responses during development.

---

## Tech Stack

- Python
- Streamlit
- Ollama
- Llama 3.2
- Pydantic
- PyPDF
- uv

---

## Project Structure

```text
ai_resume_reviewer/
│
├── app.py
├── llm_client.py
├── prompts.py
├── resume_parser.py
├── schemas.py
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

---

## File Responsibilities

### `app.py`

Handles the Streamlit user interface:

- Resume upload
- Job description input
- Buttons
- Session state
- Display results
- Download reports

### `llm_client.py`

Handles local LLM calls:

- Calls Ollama
- Sends prompts to the model
- Extracts JSON from model responses
- Validates outputs with Pydantic
- Handles errors safely

### `prompts.py`

Stores system prompts used by the LLM.

### `resume_parser.py`

Extracts and cleans text from uploaded PDF resumes.

### `schemas.py`

Defines Pydantic models for structured AI outputs.

---

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd ai_resume_reviewer
```

### 2. Create virtual environment with uv

```bash
uv venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
uv sync
```

If dependencies are not already listed, install them manually:

```bash
uv add streamlit pypdf pydantic ollama
```

---

## Ollama Setup

This project uses a local LLM through Ollama.

### 1. Install Ollama

Download Ollama from:

```text
https://ollama.com
```

### 2. Pull the model

```bash
ollama pull llama3.2
```

### 3. Confirm the model is available

```bash
ollama list
```

Expected model name:

```text
llama3.2:latest
```

---

## Run the App

```bash
uv run streamlit run app.py
```

Then open the Streamlit local URL in your browser.

---

## How to Use

1. Paste a job description
2. Upload a resume PDF
3. Check the extracted resume text
4. Click **Match Resume to Job**
5. Review:
   - Match score
   - Matched skills
   - Missing skills
   - Suggestions
6. Click **Generate Skill Gap Action Plan**
7. Download reports if needed

---

## Example Output

### Match Result

```text
Match Score: 76/100

Matched Skills
- Warehouse operations
- Inventory management
- Manual handling

Missing Skills
- Forklift licence
- Warehouse management system
- Advanced Excel

Suggestions
- Add more measurable warehouse achievements
- Mention inventory tools if used
- Highlight dispatch and stock handling experience
```

### Skill Gap Action Plan

```text
Skill: Forklift Licence

Status: Not Supported

Reason:
The resume does not mention forklift operation or a forklift licence.

Suggested Resume Bullet:
Not recommended unless the candidate has real forklift experience.

Learning Action:
Consider completing forklift licence training if applying for warehouse roles that require forklift operation.
```

---

## AI Engineering Concepts Practised

This project practises several core AI engineering concepts:

- Prompt engineering
- Local LLM integration
- Structured JSON outputs
- Pydantic validation
- Defensive parsing
- Error handling
- Streamlit session state
- PDF text extraction
- Debugging LLM responses
- Safe AI-generated recommendations

---

## Important Design Decisions

### Why local Ollama instead of OpenAI?

This project currently uses Ollama because it can run locally without paid API credits.

The app architecture is flexible enough to switch to OpenAI later by updating the LLM client file.

### Why remove general resume review?

A generic resume score is vague without a target job.

This app focuses on resume-to-job matching because resume quality depends on the role being applied for.

### Why use Pydantic?

LLM outputs can be inconsistent.

Pydantic ensures that model responses match the expected structure before the app displays them.

### Why use session state?

Streamlit reruns the script whenever a button is clicked.

`st.session_state` keeps the job match result and skill gap action plan available across reruns.

---

## Current Limitations

- PDF extraction may not perfectly preserve formatting
- Local LLM output quality depends on the Ollama model used
- The app does not use embeddings yet
- The app does not store user history in a database
- The app does not support DOCX resumes yet
- The app does not provide ATS keyword scoring yet

---

## Future Improvements

Possible next versions:

- Add DOCX resume support
- Add ATS keyword matching
- Add embeddings-based similarity scoring
- Add resume section detection
- Add export to PDF
- Add OpenAI API option
- Add job application assistant workflow
- Add cover letter generation
- Add resume version comparison
- Add persistent storage with PostgreSQL

---

## Learning Reflection

This project helped me move from traditional backend development into AI application development.

The most important lesson was that LLM output is not always reliable by default. A production-style AI app needs:

```text
Clear prompts
↓
Structured output
↓
JSON parsing
↓
Schema validation
↓
Debugging
↓
Safe error handling
```

This project is my first completed AI engineering application using a local LLM.