from __future__ import annotations
from typing import List, Literal, Dict, Any
from pydantic import BaseModel, Field
from canvas_agent.openai_tools import (
    function_tool,
    get_canvas,
    CANVAS_API_URL,
    CANVAS_API_TOKEN,
)
from typing import List, Optional, Literal, Dict, Any
import requests

# ───────────────────────────────────────────────────────────────────────────────
# P Y D A N T I C   M O D E L S (all forbid extras)
# ───────────────────────────────────────────────────────────────────────────────


class _Config:
    model_config = {"extra": "forbid"}


class Answer(BaseModel):
    text: str
    weight: Optional[int] = None
    comments: Optional[str] = None


class QuizQuestionCreate(BaseModel):
    """
    Pydantic model for creating a new quiz question.
    """
    question_name: str
    question_text: str
    question_type: Literal[
        "calculated_question", "essay_question", "file_upload_question",
        "fill_in_multiple_blanks_question", "matching_question", "multiple_answers_question",
        "multiple_choice_question", "multiple_dropdowns_question", "numerical_question",
        "short_answer_question", "text_only_question", "true_false_question"
    ]
    quiz_group_id: Optional[int] = None
    position: Optional[int] = None
    points_possible: Optional[int] = None
    correct_comments: Optional[str] = None
    incorrect_comments: Optional[str] = None
    neutral_comments: Optional[str] = None
    text_after_answers: Optional[str] = None
    answers: Optional[List[Answer]] = None


QuizQuestionCreate.model_rebuild()


class QuizQuestionUpdate(BaseModel):
    """
    Pydantic model for updating a quiz question.
    All fields are optional — only the fields to change need to be provided.
    """
    question_name: Optional[str] = None
    question_text: Optional[str] = None
    question_type: Optional[
        Literal[
            "calculated_question", "essay_question", "file_upload_question",
            "fill_in_multiple_blanks_question", "matching_question", "multiple_answers_question",
            "multiple_choice_question", "multiple_dropdowns_question", "numerical_question",
            "short_answer_question", "text_only_question", "true_false_question"
        ]
    ] = None
    quiz_group_id: Optional[int] = None
    position: Optional[int] = None
    points_possible: Optional[int] = None
    correct_comments: Optional[str] = None
    incorrect_comments: Optional[str] = None
    neutral_comments: Optional[str] = None
    text_after_answers: Optional[str] = None
    # assuming you defined Answer before
    answers: Optional[List["Answer"]] = None


QuizQuestionUpdate.model_rebuild()


@function_tool()
def list_quiz_questions(
    course_id: int,
    quiz_id: int,
    quiz_submission_id: int,
    quiz_submission_attempt: int,
) -> List[Dict[str, Any]]:
    """
    List questions for a quiz or a specific submission.

    Args:
        course_id (int): The ID of the course.
        quiz_id (int): The ID of the quiz.
        quiz_submission_id (int): ID of the quiz submission. Pass 0 to skip.
        quiz_submission_attempt (int): Attempt number for the submission. Pass 0 to skip.

    Returns:
        List[dict]: List of slim quiz question objects.
    """
    canvas = get_canvas()
    url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/quizzes/{quiz_id}/questions"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}

    params = {}
    if quiz_submission_id != 0:
        params["quiz_submission_id"] = quiz_submission_id
    if quiz_submission_attempt != 0:
        params["quiz_submission_attempt"] = quiz_submission_attempt

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Error fetching quiz questions: {response.status_code} - {response.text}"
        )

    questions = response.json()
    return questions


@function_tool()
def get_quiz_question(
    course_id: int,
    quiz_id: int,
    question_id: int,
) -> Dict[str, Any]:
    """
    Get a single quiz question.

    Args:
        course_id (int)
        quiz_id (int)
        question_id (int)

    Returns:
        dict: Full question object.
    """
    canvas = get_canvas()
    url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/quizzes/{quiz_id}/questions/{question_id}"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Error fetching quiz question: {response.status_code} - {response.text}"
        )

    quiz_question = response.json()
    return quiz_question


@function_tool()
def create_quiz_question(course_id: int, quiz_id: int, question_data: QuizQuestionCreate) -> Dict[str, Any]:
    """
    Create a new quiz question using direct REST API call to Canvas.
    """
    url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/quizzes/{quiz_id}/questions"
    headers = {
        "Authorization": f"Bearer {CANVAS_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "question": question_data.model_dump(exclude_unset=True)
    }

    response = requests.post(url, headers=headers, json=payload)

    if not response.ok:
        raise Exception(
            f"Failed to create quiz question: {response.status_code} - {response.text}")

    data = response.json()

    return {
        "id": data["id"],
        "question_name": data.get("question_name"),
        "question_text": data.get("question_text"),
        "question_type": data.get("question_type"),
        "points_possible": data.get("points_possible"),
        "position": data.get("position"),
    }


@function_tool()
def update_quiz_question(
    course_id: int,
    quiz_id: int,
    question_id: int,
    data: QuizQuestionUpdate,
) -> Dict[str, Any]:
    """
    Update an existing quiz question in a Canvas quiz.

    Args:
        course_id (int): ID of the course.
        quiz_id (int): ID of the quiz.
        question_id (int): ID of the question to update.
        data (QuizQuestionUpdate): Fields to update.

    Returns:
        dict: The updated question object.
    """
    url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/quizzes/{quiz_id}/questions/{question_id}"
    headers = {
        "Authorization": f"Bearer {CANVAS_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "question": data.model_dump(exclude_unset=True)
    }

    response = requests.put(url, headers=headers, json=payload)

    if not response.ok:
        raise Exception(
            f"Failed to update quiz question: {response.status_code} - {response.text}"
        )

    return response.json()


@function_tool()
def delete_quiz_question(
    course_id: int,
    quiz_id: int,
    question_id: int,
) -> Dict[str, Any]:
    """
    Delete a quiz question from a Canvas quiz.

    Args:
        course_id (int): ID of the course.
        quiz_id (int): ID of the quiz.
        question_id (int): ID of the question to delete.

    Returns:
        dict: A dictionary indicating the deletion status, like {'id': ..., 'deleted': True}.
    """
    url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/quizzes/{quiz_id}/questions/{question_id}"
    headers = {
        "Authorization": f"Bearer {CANVAS_API_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.delete(url, headers=headers)

    if not response.ok:
        raise Exception(
            f"Failed to delete quiz question: {response.status_code} - {response.text}"
        )

    # Canvas usually returns 204 No Content after a delete
    # so we'll just return success manually
    return {
        "id": question_id,
        "deleted": True
    }
