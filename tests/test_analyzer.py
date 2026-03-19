import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from unittest.mock import patch, MagicMock
from analyzer import _parse, _call, score_resume, generate_interview_qa, rewrite_bullets, generate_report, analyze_full


# ── _parse() tests ─────────────────────────────────────────────────────────────

def test_parse_valid_json():
    raw = '{"ats_score": 75, "skill_match_percent": 60}'
    result = _parse(raw)
    assert result["ats_score"] == 75
    assert result["skill_match_percent"] == 60

def test_parse_with_markdown_fences():
    raw = '```json\n{"ats_score": 80}\n```'
    result = _parse(raw)
    assert result["ats_score"] == 80

def test_parse_with_preamble():
    raw = 'Here is the JSON:\n{"ats_score": 90}'
    result = _parse(raw)
    assert result["ats_score"] == 90

def test_parse_malformed_returns_error():
    raw = "this is not json at all!!!"
    result = _parse(raw)
    assert "error" in result

def test_parse_empty_string():
    result = _parse("")
    assert "error" in result

def test_parse_nested_json():
    raw = '{"scores": {"ats": 70}, "gaps": ["Python", "FastAPI"]}'
    result = _parse(raw)
    assert result["scores"]["ats"] == 70
    assert "Python" in result["gaps"]


# ── score_resume() tests ───────────────────────────────────────────────────────

MOCK_SCORE = {
    "ats_score": 72,
    "skill_match_percent": 65,
    "tone_score": 80,
    "matched_skills": ["Python", "FastAPI"],
    "skill_gaps": [
        {"skill": "Docker", "suggestion": "Learn Docker basics"},
        {"skill": "PostgreSQL", "suggestion": "Practice SQL queries"},
        {"skill": "AWS", "suggestion": "Try AWS free tier"}
    ]
}

@patch("analyzer._call")
def test_score_resume_returns_dict(mock_call):
    mock_call.return_value = '{"ats_score": 72, "skill_match_percent": 65, "tone_score": 80, "matched_skills": ["Python"], "skill_gaps": [{"skill": "Docker", "suggestion": "Learn Docker"}]}'
    result = score_resume("Python developer", "FastAPI developer needed")
    assert isinstance(result, dict)

@patch("analyzer._call")
def test_score_resume_has_required_keys(mock_call):
    import json
    mock_call.return_value = json.dumps(MOCK_SCORE)
    result = score_resume("Python developer", "FastAPI developer needed")
    assert "ats_score" in result
    assert "skill_match_percent" in result
    assert "tone_score" in result
    assert "matched_skills" in result
    assert "skill_gaps" in result

@patch("analyzer._call")
def test_score_resume_ats_score_range(mock_call):
    import json
    mock_call.return_value = json.dumps(MOCK_SCORE)
    result = score_resume("Python developer", "FastAPI developer needed")
    assert 0 <= result["ats_score"] <= 100

@patch("analyzer._call")
def test_score_resume_skill_gaps_is_list(mock_call):
    import json
    mock_call.return_value = json.dumps(MOCK_SCORE)
    result = score_resume("Python developer", "FastAPI developer needed")
    assert isinstance(result["skill_gaps"], list)


# ── generate_interview_qa() tests ─────────────────────────────────────────────

MOCK_INTERVIEW = {
    "questions": [
        {
            "question": "Tell me about a time you built an API",
            "situation": "During ShipSense project",
            "task": "Build a delay prediction API",
            "action": "Used FastAPI and Random Forest",
            "result": "Achieved 85% accuracy"
        }
    ] * 5
}

@patch("analyzer._call")
def test_interview_qa_returns_dict(mock_call):
    import json
    mock_call.return_value = json.dumps(MOCK_INTERVIEW)
    result = generate_interview_qa("Python developer", "FastAPI developer needed")
    assert isinstance(result, dict)

@patch("analyzer._call")
def test_interview_qa_has_questions_key(mock_call):
    import json
    mock_call.return_value = json.dumps(MOCK_INTERVIEW)
    result = generate_interview_qa("Python developer", "FastAPI developer needed")
    assert "questions" in result

@patch("analyzer._call")
def test_interview_qa_questions_have_star_format(mock_call):
    import json
    mock_call.return_value = json.dumps(MOCK_INTERVIEW)
    result = generate_interview_qa("Python developer", "FastAPI developer needed")
    for q in result["questions"]:
        assert "question" in q
        assert "situation" in q
        assert "action" in q
        assert "result" in q


# ── rewrite_bullets() tests ───────────────────────────────────────────────────

MOCK_REWRITES = {
    "rewrites": [
        {
            "before": "Worked on ML models",
            "after": "Engineered Random Forest model achieving 85% accuracy",
            "why": "Added specific metric and action verb"
        },
        {
            "before": "Did data analysis",
            "after": "Performed EDA on 50k+ records using pandas and seaborn",
            "why": "Quantified scale and named tools"
        },
        {
            "before": "Used FastAPI",
            "after": "Deployed ML model as real-time REST API using FastAPI",
            "why": "Added context and impact"
        }
    ]
}

@patch("analyzer._call")
def test_rewrite_bullets_returns_dict(mock_call):
    import json
    mock_call.return_value = json.dumps(MOCK_REWRITES)
    result = rewrite_bullets("Python developer", "FastAPI developer needed")
    assert isinstance(result, dict)

@patch("analyzer._call")
def test_rewrite_bullets_has_rewrites_key(mock_call):
    import json
    mock_call.return_value = json.dumps(MOCK_REWRITES)
    result = rewrite_bullets("Python developer", "FastAPI developer needed")
    assert "rewrites" in result

@patch("analyzer._call")
def test_rewrite_bullets_each_has_before_after_why(mock_call):
    import json
    mock_call.return_value = json.dumps(MOCK_REWRITES)
    result = rewrite_bullets("Python developer", "FastAPI developer needed")
    for rw in result["rewrites"]:
        assert "before" in rw
        assert "after" in rw
        assert "why" in rw


# ── analyze_full() tests ──────────────────────────────────────────────────────

@patch("analyzer.generate_report")
@patch("analyzer.rewrite_bullets")
@patch("analyzer.generate_interview_qa")
@patch("analyzer.score_resume")
def test_analyze_full_returns_all_keys(mock_score, mock_interview, mock_rewrites, mock_report):
    mock_score.return_value = MOCK_SCORE
    mock_interview.return_value = MOCK_INTERVIEW
    mock_rewrites.return_value = MOCK_REWRITES
    mock_report.return_value = {"report_markdown": "# Report", "linkedin_about": "Hi I am..."}

    result = analyze_full("Python developer", "FastAPI developer needed")
    assert "scores" in result
    assert "interview_qa" in result
    assert "rewrites" in result
    assert "report" in result

@patch("analyzer.generate_report")
@patch("analyzer.rewrite_bullets")
@patch("analyzer.generate_interview_qa")
@patch("analyzer.score_resume")
def test_analyze_full_calls_all_functions(mock_score, mock_interview, mock_rewrites, mock_report):
    mock_score.return_value = MOCK_SCORE
    mock_interview.return_value = MOCK_INTERVIEW
    mock_rewrites.return_value = MOCK_REWRITES
    mock_report.return_value = {"report_markdown": "# Report", "linkedin_about": "Hi"}

    analyze_full("resume text", "job description")
    mock_score.assert_called_once()
    mock_interview.assert_called_once()
    mock_rewrites.assert_called_once()
    mock_report.assert_called_once()