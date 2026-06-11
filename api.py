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
        "profile_id": payload.get("profile_id", ""),
        "candidate_name": "",
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


def build_prompt(profile, inspected_fields):
    return f"""
You are an autofill assistant for job application forms.

You will receive:
1. A candidate profile from Supabase.
2. A list of inspected form fields from the user's current browser page.

Your task:
Return a JSON object with fillable_fields only.

Each fillable field must include:
source_index
visible_label
field_type
answer

Rules:
- Do not invent information.
- If unsure, leave answer empty.
- Do not submit forms.
- Do not fill passwords.
- Do not fill sensitive legal declarations unless clearly present in the profile.
- Keep answers concise.
- Match fields using visible_label, name, id, placeholder and context.

Candidate profile:
{profile}

Inspected fields:
{inspected_fields}

Return only valid JSON in this format:

{{
  "status": "success",
  "fillable_count": 0,
  "fillable_fields": [
    {{
      "source_index": 0,
      "visible_label": "",
      "field_type": "",
      "answer": ""
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

    prompt = build_prompt(profile, payload.inspected_fields)

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
