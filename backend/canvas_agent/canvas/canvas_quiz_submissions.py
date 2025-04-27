"""
QUIZ-SUBMISSION TOOLS  — strict‐schema compliant
"""

from __future__ import annotations
from typing import List, Literal, Dict, Any
from pydantic import BaseModel, Field
from canvas_agent.openai_tools import (
    function_tool,
    get_canvas,
    CANVAS_API_URL,
    CANVAS_API_TOKEN,
)
import requests

# ───────────────────────────────────────────────────────────────────────────────
# P Y D A N T I C   M O D E L S (all forbid extras)
# ───────────────────────────────────────────────────────────────────────────────


class _Config:
    model_config = {"extra": "forbid"}


class QuizSubmissionStart(BaseModel, _Config):
    access_code: str = Field("", description="Access code, or empty")
    preview: bool = Field(False, description="True => preview mode")


class QuestionUpdate(BaseModel):
    score: float = Field(..., description="New score")
    comment: str = Field(..., description="New comment")


class QuestionUpdateItem(BaseModel):
    question_id: str = Field(..., description="Question ID as string")
    update: QuestionUpdate


class QuizSubmissionUpdate(BaseModel, _Config):
    """One element for the update endpoint."""
    attempt: int
    fudge_points: float = 0.0
    questions: List[QuestionUpdateItem] = Field(
        [], description="List of question updates"
    )


class QuizSubmissionComplete(BaseModel, _Config):
    attempt: int = Field(..., description="Attempt number to complete")
    validation_token: str = Field(..., description="Token from start response")
    access_code: str = Field("", description="Access code, or empty")


# ───────────────────────────────────────────────────────────────────────────────
# I N T E R N A L   H E L P E R S
# ───────────────────────────────────────────────────────────────────────────────

def _api_request(
    method: str, path: str, json: dict | None = None
) -> Dict[str, Any]:
    url = f"{CANVAS_API_URL}/api/v1/{path.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {CANVAS_API_TOKEN}",
        "Content-Type": "application/json",
    }
    r = requests.request(method, url, headers=headers, json=json)
    if r.status_code >= 400:
        raise RuntimeError(f"Canvas API error {r.status_code}: {r.text}")
    return r.json()


def _brief(qs) -> Dict[str, Any]:
    """
    Normalize a quiz-submission record. Handles both Canvas objects and raw dicts.
    """
    if isinstance(qs, dict):
        return {
            "id": qs.get("id"),
            "user_id": qs.get("user_id"),
            "attempt": qs.get("attempt"),
            "score": qs.get("score"),
            "kept_score": qs.get("kept_score"),
            "started_at": qs.get("started_at"),
            "finished_at": qs.get("finished_at"),
            "workflow_state": qs.get("workflow_state"),
        }
    else:
        # Canvas object with attributes
        return {
            "id": qs.id,
            "user_id": qs.user_id,
            "attempt": qs.attempt,
            "score": qs.score,
            "kept_score": getattr(qs, "kept_score", None),
            "started_at": qs.started_at,
            "finished_at": qs.finished_at,
            "workflow_state": qs.workflow_state,
        }


# ───────────────────────────────────────────────────────────────────────────────
# T O O L   F U N C T I O N S
# ───────────────────────────────────────────────────────────────────────────────


@function_tool()
def list_quiz_submissions(
    course_id: int,
    quiz_id: int,
    include: List[Literal["submission", "quiz", "user"]],
) -> List[Dict[str, Any]]:
    """
    List all submissions for a quiz.

    Args:
        course_id (int)
        quiz_id (int)
        include (List[str]): 'submission','quiz','user'; pass [] to skip.

    Returns:
        List[dict]: Brief quiz-submission objects.
    """
    params = {"include": include} if include else None
    resp = _api_request(
        "GET",
        f"courses/{course_id}/quizzes/{quiz_id}/submissions",
        json=params,
    )
    return [_brief(s) for s in resp["quiz_submissions"]]


@function_tool()
def get_my_quiz_submission(
    course_id: int,
    quiz_id: int,
    include: List[Literal["submission", "quiz", "user"]],
) -> Dict[str, Any]:
    """
    Get the current user's submission.

    Args:
        course_id (int)
        quiz_id (int)
        include (List[str]): 'submission','quiz','user'; pass [] to skip.

    Returns:
        dict: Brief submission.
    """
    params = {"include": include} if include else None
    resp = _api_request(
        "GET",
        f"courses/{course_id}/quizzes/{quiz_id}/submission",
        json=params,
    )
    return _brief(resp["quiz_submissions"][0])


@function_tool()
def get_quiz_submission(
    course_id: int,
    quiz_id: int,
    submission_id: int,
    include: List[Literal["submission", "quiz", "user"]],
) -> Dict[str, Any]:
    """
    Get a specific submission by ID.

    Args:
        course_id (int)
        quiz_id (int)
        submission_id (int)
        include (List[str]): 'submission','quiz','user'; pass [] to skip.

    Returns:
        dict: Brief submission.
    """
    params = {"include": include} if include else None
    resp = _api_request(
        "GET",
        f"courses/{course_id}/quizzes/{quiz_id}/submissions/{submission_id}",
        json=params,
    )
    return _brief(resp["quiz_submissions"][0])


@function_tool()
def start_quiz_submission(
    course_id: int,
    quiz_id: int,
    access_code: str,
    preview: bool,
) -> Dict[str, Any]:
    """
    Start or preview a quiz submission.

    Args:
        course_id (int)
        quiz_id (int)
        access_code (str): Access code (empty string if none)
        preview (bool): True to open in preview mode

    Returns:
        dict: Brief new submission.
    """
    payload: Dict[str, Any] = {}
    if access_code:
        payload["access_code"] = access_code
    if preview:
        payload["preview"] = True

    resp = _api_request(
        "POST",
        f"courses/{course_id}/quizzes/{quiz_id}/submissions",
        json=payload or None,
    )
    return _brief(resp["quiz_submissions"][0])


@function_tool()
def update_quiz_submission(
    course_id: int,
    quiz_id: int,
    submission_id: int,
    attempt: int,
    fudge_points: float,
    questions: List[QuestionUpdateItem],
) -> Dict[str, Any]:
    """
    Adjust scores/comments or fudge points for one quiz submission attempt.

    Args:
        course_id (int)
        quiz_id (int)
        submission_id (int)
        attempt (int): Attempt number to update.
        fudge_points (float): Points adjustment (±).
        questions (List[QuestionUpdateItem]): One item per question:
            - question_id (str)
            - update (QuestionUpdate)

    Returns:
        dict: Brief updated submission.
    """
    # build the single-element payload:
    qmap = {
        item.question_id: item.update.model_dump(exclude_none=True)
        for item in questions
    }
    payload = {
        "quiz_submissions": [{
            "attempt": attempt,
            "fudge_points": fudge_points,
            "questions": qmap
        }]
    }

    _api_request(
        "PUT",
        f"courses/{course_id}/quizzes/{quiz_id}/submissions/{submission_id}",
        json=payload,
    )
    return get_quiz_submission(course_id, quiz_id, submission_id)


@function_tool()
def complete_quiz_submission(
    course_id: int,
    quiz_id: int,
    submission_id: int,
    attempt: int,
    validation_token: str,
    access_code: str,
) -> Dict[str, Any]:
    """
    Complete and grade a quiz submission.

    Args:
        course_id (int)
        quiz_id (int)
        submission_id (int)
        attempt (int): The attempt number to complete (must be latest).
        validation_token (str): Token received when submission was started.
        access_code (str): Access code if required (empty string if none).

    Returns:
        dict: Brief submission after completion.
    """
    payload: Dict[str, Any] = {
        "attempt": attempt,
        "validation_token": validation_token,
    }
    if access_code:
        payload["access_code"] = access_code

    _api_request(
        "POST",
        f"courses/{course_id}/quizzes/{quiz_id}/submissions/{submission_id}/complete",
        json={"quiz_submissions": [payload]},
    )
    return get_quiz_submission(course_id, quiz_id, submission_id)


@function_tool()
def quiz_submission_time(
    course_id: int, quiz_id: int, submission_id: int
) -> Dict[str, Any]:
    """
    Get timing info for an in-progress attempt.

    Args:
        course_id (int)
        quiz_id (int)
        submission_id (int)

    Returns:
        dict: {'end_at': str, 'time_left': int}
    """
    return _api_request(
        "GET",
        f"courses/{course_id}/quizzes/{quiz_id}/submissions/{submission_id}/time",
    )
