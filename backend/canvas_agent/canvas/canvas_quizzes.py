"""
QUIZ TOOLS
==========

A *methodical, agent-ready* replica of the assignment tool set, adapted for
Canvas *quizzes*.  The same overall shape and design choices are preserved:

* Pydantic models for validation (`QuizCreate`, `QuizEdit`)
* Minimal, predictable doc-strings (for function-calling agents)
* Slimmed-down return payloads (dict / list[dict] or success strings)
* Direct use of the Canvas API endpoints when needed
"""

from typing import Optional, List, Literal, Dict, Any
import requests
from pydantic import BaseModel

from canvas_agent.openai_tools import (
    function_tool,
    get_canvas,
    CANVAS_API_URL,
    CANVAS_API_TOKEN,
)

# ────────────────────────────────────────────────────────────────────────────────
# P Y D A N T I C   M O D E L S
# ────────────────────────────────────────────────────────────────────────────────


class QuizCreate(BaseModel):
    """Pydantic model for creating a new Canvas quiz."""

    title: str  # required

    description: Optional[str] = None
    quiz_type: Optional[
        Literal["practice_quiz", "assignment", "graded_survey", "survey"]
    ] = None

    assignment_group_id: Optional[int] = None
    time_limit: Optional[int] = None
    shuffle_answers: Optional[bool] = None

    hide_results: Optional[Literal["always",
                                   "until_after_last_attempt"]] = None
    show_correct_answers: Optional[bool] = None
    show_correct_answers_last_attempt: Optional[bool] = None
    show_correct_answers_at: Optional[str] = None  # ISO‐8601
    hide_correct_answers_at: Optional[str] = None  # ISO‐8601

    allowed_attempts: Optional[int] = None
    scoring_policy: Optional[Literal["keep_highest", "keep_latest"]] = None

    one_question_at_a_time: Optional[bool] = None
    cant_go_back: Optional[bool] = None

    access_code: Optional[str] = None
    ip_filter: Optional[str] = None

    due_at: Optional[str] = None  # ISO‐8601
    lock_at: Optional[str] = None  # ISO‐8601
    unlock_at: Optional[str] = None  # ISO‐8601

    published: Optional[bool] = None
    one_time_results: Optional[bool] = None
    only_visible_to_overrides: Optional[bool] = None


class QuizEdit(QuizCreate):
    """All fields optional when editing an existing quiz."""
    title: Optional[str] = None


# ────────────────────────────────────────────────────────────────────────────────
# H E L P E R S
# ────────────────────────────────────────────────────────────────────────────────


def _request(
    method: str, path: str, json: Optional[dict] = None
) -> Dict[str, Any]:
    url = f"{CANVAS_API_URL}/api/v1/{path.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {CANVAS_API_TOKEN}",
        "Content-Type": "application/json",
    }
    resp = requests.request(method, url, headers=headers, json=json)
    if resp.status_code >= 400:
        raise RuntimeError(f"Canvas API error {resp.status_code}: {resp.text}")
    return resp.json()


def _simplify_quiz(q) -> Dict[str, Any]:
    """Return only the most relevant quiz fields for list / get."""
    return {
        "id": q.id,
        "title": q.title,
        "quiz_type": q.quiz_type,
        "points_possible": getattr(q, "points_possible", None),
        "due_at": q.due_at,
        "published": q.published,
        "html_url": q.html_url,
    }


# ────────────────────────────────────────────────────────────────────────────────
# T O O L   F U N C T I O N S
# ────────────────────────────────────────────────────────────────────────────────


@function_tool()
def list_quizzes(course_id: int) -> List[Dict[str, Any]]:
    """
    List quizzes in a course.

    Args:
        course_id (int): Canvas course ID.

    Returns:
        List[Dict[str, Any]]: Each item has keys:
            id, title, quiz_type, points_possible, due_at, published, html_url
    """
    canvas = get_canvas()
    quizzes = canvas.get_course(course_id).get_quizzes()
    return [_simplify_quiz(q) for q in quizzes]


@function_tool()
def get_quiz(course_id: int, quiz_id: int) -> Dict[str, Any]:
    """
    Get a single quiz.

    Args:
        course_id (int): Course ID.
        quiz_id (int): Quiz ID.

    Returns:
        Dict[str, Any]: Same keys as list_quizzes plus description.
    """
    canvas = get_canvas()
    q = canvas.get_course(course_id).get_quiz(quiz_id)
    data = _simplify_quiz(q)
    data["description"] = q.description
    return data


@function_tool()
def create_quiz(course_id: int, quiz_data: QuizCreate) -> str:
    """
    Create a quiz.

    Args:
        course_id (int): Course ID.
        quiz_data (QuizCreate): Quiz parameters.

    Returns:
        str: "Successfully created quiz."
    """
    payload = {"quiz": quiz_data.model_dump(exclude_none=True)}
    _request("POST", f"courses/{course_id}/quizzes", json=payload)
    return "Successfully created quiz."


@function_tool()
def edit_quiz(course_id: int, quiz_id: int, quiz_data: QuizEdit) -> Dict[str, Any]:
    """
    Edit a quiz.

    Args:
        course_id (int): Course ID.
        quiz_id (int): Quiz ID.
        quiz_data (QuizEdit): Fields to change.

    Returns:
        Dict[str, Any]: Updated quiz (simplified).
    """
    payload = {"quiz": quiz_data.model_dump(exclude_none=True)}
    _request("PUT", f"courses/{course_id}/quizzes/{quiz_id}", json=payload)
    return get_quiz(course_id, quiz_id)


@function_tool()
def delete_quiz(course_id: int, quiz_id: int) -> Dict[str, Any]:
    """
    Delete a quiz.

    Args:
        course_id (int): Course ID.
        quiz_id (int): Quiz ID.

    Returns:
        Dict[str, Any]: {'id': quiz_id, 'deleted': True}
    """
    _request("DELETE", f"courses/{course_id}/quizzes/{quiz_id}")
    return {"id": quiz_id, "deleted": True}


class OrderItem(BaseModel):
    id: int
    type: Literal["question", "group"]

    model_config = {"extra": "forbid"}


@function_tool()
def reorder_quiz_items(
    course_id: int,
    quiz_id: int,
    order: List[OrderItem],  # ← use the model
) -> str:
    """
    Re-order quiz questions/groups.

    Args:
        course_id (int): Course ID.
        quiz_id (int): Quiz ID.
        order (List[dict]): Each dict: {'id': <int>, 'type': 'question' | 'group'}

    Returns:
        str: "Successfully reordered quiz items."
    """
    payload = {"order": [item.model_dump() for item in order]}
    _request(
        "POST", f"courses/{course_id}/quizzes/{quiz_id}/reorder", json=payload)
    return "Successfully reordered quiz items."


@function_tool()
def validate_quiz_access_code(
    course_id: int, quiz_id: int, access_code: str
) -> bool:
    """
    Validate a quiz access code.

    Args:
        course_id (int): Course ID.
        quiz_id (int): Quiz ID.
        access_code (str): Access code to validate.

    Returns:
        bool: True if access code is valid.
    """
    payload = {"access_code": access_code}
    resp = _request(
        "POST",
        f"courses/{course_id}/quizzes/{quiz_id}/validate_access_code",
        json=payload,
    )
    # Canvas returns {'valid': true/false, ...}
    return bool(resp.get("valid", False))
