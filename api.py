import os
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


app = FastAPI(title="SponsorSearchUK Autofill API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FillPackageRequest(BaseModel):
    application_url: str
    inspected_fields: List[Dict[str, Any]]
    profile_id: Optional[str] = None


@app.get("/")
def health_check():
    return {
        "status": "success",
        "message": "SponsorSearchUK Autofill API is running"
    }

@app.post("/analyze-form")
def analyze_form(payload: dict):
    return {
        "status": "received",
        "profile_id": payload.get("profile_id", "default_profile"),
        "candidate_name": "Candidate",
        "application_url": payload.get("application_url", "")
    }


@app.post("/detect-form-behaviour")
def detect_form_behaviour(payload: dict):
    return {
        "status": "success",
        "form_behavior": "standard_application_form"
    }


@app.post("/inspect-form")
def inspect_form(payload: dict):
    return {
        "status": "success",
        "field_count": 0,
        "fields_preview": []
    }


@app.post("/classify-fields")
def classify_fields(payload: dict):
    return {
        "status": "success",
        "classified_count": 0,
        "classified_fields": []
    }


@app.post("/resolve-fields")
def resolve_fields(payload: dict):
    return {
        "status": "success",
        "resolved_count": 0,
        "resolved_fields": []
    }


@app.post("/generate-answers")
def generate_answers(payload: dict):
    return {
        "status": "success",
        "generated_count": 0,
        "generated_answers": []
    }


@app.post("/get-resolved-fill-package")
def get_resolved_fill_package(payload: dict):
    return {
        "status": "success",
        "fillable_count": 0,
        "fillable_fields": []
    }

def get_profile(profile_id: Optional[str] = None):
    query = supabase.table("profiles").select("*")

    if profile_id:
        result = query.eq("profile_id", profile_id).limit(1).execute()
    else:
        result = query.order("created_at", desc=True).limit(1).execute()

    if not result.data:
        return None

    return result.data[0]


def build_prompt(profile, inspected_fields, application_url):
    return f"""
You are an AI autofill engine for job application forms.

You receive:
1. A complete candidate profile JSON from Supabase.
2. A list of inspected form fields from the user's current browser page.
3. The application URL.

Your job is to create a fill package that can be safely inserted into the visible application form.

Use the entire candidate profile as the source of truth, including:
- profile_metadata
- personal_identity
- contact
- work_authorization
- career_intent
- professional_summary
- skills
- work_experience
- education
- projects
- documents
- application_question_bank
- preferences
- retrieval_metadata

You may fill fields for:
- full name
- first name
- middle name
- last name
- email
- phone
- country code
- city
- country
- current location
- LinkedIn
- portfolio
- GitHub
- personal website
- current visa status
- work authorization
- sponsorship requirement
- notice period
- availability date
- relocation preference
- preferred locations
- salary expectation
- target roles
- current job title
- current company
- previous employers
- degree
- university
- field of study
- graduation year
- skills
- tools
- projects
- achievements
- why this role
- why this company
- tell me about yourself
- sponsorship explanation
- relocation explanation
- salary expectation answer
- other open-ended application questions

Rules:
- Do not invent facts that are not supported by the profile.
- For open-ended questions, you may generate a concise answer using the profile.
- If the profile has a matching answer inside application_question_bank, prefer that.
- If the field asks for a long answer, keep it natural and specific.
- If the field asks for a short answer, keep it concise.
- Do not fill passwords.
- Do not fill captcha fields.
- Do not submit the form.
- Do not answer criminal, disability, ethnicity, gender, veteran, or equal-opportunity questions unless the profile explicitly contains a safe answer.
- Do not fill file upload fields. Mark them as needs_manual_upload.
- If unsure, return an empty answer.
File upload handling:
- If a field is for resume, CV, cover letter, portfolio or document upload, do not put it in fillable_fields.
- Add it to manual_fields.
- Reason should be "Manual upload required".
- Never use local file paths as answers.

Important:
Each inspected field has a source_index. Use that exact source_index in your output so the extension can fill the correct field.

Candidate profile JSON:
{profile}

Inspected fields:
{inspected_fields}

Application URL:
{application_url}

Return only valid JSON. No markdown. No explanation.

Required format:
{{
  "status": "success",
  "profile_id": "",
  "candidate_name": "",
  "fillable_count": 0,
  "fillable_fields": [
    {{
      "source_index": 0,
      "visible_label": "",
      "field_type": "",
      "answer": "",
      "answer_source": "profile | generated | application_question_bank | empty",
      "confidence": 0.0
    }}
  ],
  "manual_fields": [
    {{
      "source_index": 0,
      "visible_label": "",
      "reason": ""
    }}
  ]
}}
"""

@app.post("/generate-fill-package")
def generate_fill_package(payload: FillPackageRequest):
    profile = get_profile(payload.profile_id)

    if not profile:
        return {
            "status": "error",
            "message": "No candidate profile found.",
            "fillable_count": 0,
            "fillable_fields": []
        }

    prompt = build_prompt(profile, payload.inspected_fields, payload.application_url)

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "").strip()

        import json
        parsed = json.loads(raw_text)

        return parsed

    except Exception as error:
        return {
            "status": "error",
            "message": str(error),
            "fillable_count": 0,
            "fillable_fields": []
        }


@app.post("/save-autofill-result")
def save_autofill_result(payload: Dict[str, Any]):
    try:
        supabase.table("application_runs").insert(payload).execute()

        return {
            "status": "success",
            "message": "Autofill result saved."
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }
