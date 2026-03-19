import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def _call(prompt: str) -> str:
    """Make a single Groq API call and return raw text."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a JSON-only responder. Return raw JSON only. No markdown fences, no preamble, no explanation. Just the JSON object."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=2000
    )
    return response.choices[0].message.content


def _parse(raw: str) -> dict:
    """Robustly parse JSON from LLM output. Handles fences, preambles, malformed JSON."""
    # Mode 1: direct parse
    try:
        return json.loads(raw)
    except Exception:
        pass

    # Mode 2: strip markdown fences
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Mode 3: extract first {...} block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    # Fallback: return error dict
    return {"error": "Failed to parse LLM response", "raw": raw}


def score_resume(resume_text: str, job_description: str) -> dict:
    """
    Returns ATS score, skill match %, tone score, matched skills, and skill gaps.
    """
    prompt = f"""
Analyze this resume against the job description.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_description[:2000]}

Return this exact JSON structure:
{{
  "ats_score": <integer 0-100>,
  "skill_match_percent": <integer 0-100>,
  "tone_score": <integer 0-100>,
  "matched_skills": ["skill1", "skill2", "skill3"],
  "skill_gaps": [
    {{"skill": "skill name", "suggestion": "how to learn or demonstrate this skill"}}
  ]
}}

Rules:
- ats_score: how well resume passes ATS keyword matching
- skill_match_percent: percentage of JD required skills found in resume
- tone_score: professionalism and impact of language (0-100)
- matched_skills: list of skills present in BOTH resume and JD
- skill_gaps: minimum 3 skills from JD missing in resume, each with a learning suggestion
"""
    raw = _call(prompt)
    return _parse(raw)


def generate_interview_qa(resume_text: str, job_description: str) -> dict:
    """
    Returns exactly 5 STAR-format interview questions with answers.
    """
    prompt = f"""
Based on this resume and job description, generate exactly 5 interview questions with STAR-format answers.

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{job_description[:1500]}

Return this exact JSON structure:
{{
  "questions": [
    {{
      "question": "Tell me about a time when...",
      "situation": "Describe the situation...",
      "task": "What was your task...",
      "action": "What actions did you take...",
      "result": "What was the outcome..."
    }}
  ]
}}

Generate exactly 5 questions. Make them specific to the resume and JD.
"""
    raw = _call(prompt)
    return _parse(raw)


def rewrite_bullets(resume_text: str, job_description: str) -> dict:
    """
    Returns 3 bullet point rewrites with before/after/why.
    """
    prompt = f"""
Find 3 weak bullet points from this resume and rewrite them to better match the job description.

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{job_description[:1000]}

Return this exact JSON structure:
{{
  "rewrites": [
    {{
      "before": "original bullet point text",
      "after": "improved bullet point text",
      "why": "explanation of what was improved"
    }}
  ]
}}

Generate exactly 3 rewrites. Focus on quantifying achievements and using JD keywords.
"""
    raw = _call(prompt)
    return _parse(raw)


def generate_report(resume_text: str, job_description: str, score_data: dict) -> dict:
    """
    Returns a full Markdown coaching report with LinkedIn About draft.
    """
    prompt = f"""
Generate a comprehensive coaching report for this job applicant.

RESUME SUMMARY:
{resume_text[:1500]}

JOB DESCRIPTION:
{job_description[:1000]}

ATS SCORE: {score_data.get('ats_score', 'N/A')}
SKILL MATCH: {score_data.get('skill_match_percent', 'N/A')}%

Return this exact JSON structure:
{{
  "report_markdown": "# Resume Coaching Report\\n\\n## Overall Assessment\\n...full markdown report...",
  "linkedin_about": "LinkedIn About section draft (300 words max, first person, professional)"
}}

The report_markdown must include these sections:
- Overall Assessment
- Key Strengths
- Areas for Improvement
- Action Plan (3 concrete steps)
- Final Recommendations
"""
    raw = _call(prompt)
    return _parse(raw)


def analyze_full(resume_text: str, job_description: str) -> dict:
    """
    Runs all 4 analyses and returns combined result.
    This is the main function called by FastAPI.
    """
    scores = score_resume(resume_text, job_description)
    interview = generate_interview_qa(resume_text, job_description)
    rewrites = rewrite_bullets(resume_text, job_description)
    report = generate_report(resume_text, job_description, scores)

    return {
        "scores": scores,
        "interview_qa": interview,
        "rewrites": rewrites,
        "report": report
    }