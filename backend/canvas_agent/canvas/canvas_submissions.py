"""
Submit an assignment
List assignment submissions
List submissions for multiple assignments
Get a single submission
Get a single submission by anonymous id
Upload a file
Grade or comment on a submission
Grade or comment on a submission by anonymous id
List gradeable students
List multiple assignments gradeable students
Grade or comment on multiple submissions
Mark submission as read
Mark submission as unread
Mark bulk submissions as read
Mark submission item as read
Clear unread status for all submissions
Get rubric assessments read state
Mark rubric assessments as read
Get document annotations read state
Mark document annotations as read
Submission Summary
"""
from canvas_agent.openai_tools import *


@function_tool()
def get_submissions(course_id: int, assignment_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve all submissions for a specific assignment in a Canvas course.

    This function calls the Canvas API to fetch every submission record for 
    the given assignment. It then returns a clean list of dictionaries containing 
    the most relevant information about each submission, such as the student’s 
    user ID, user name, submission status, grade, score, timestamps, and a preview URL.

    Args:
        course_id (int): The Canvas course ID containing the assignment.
        assignment_id (int): The ID of the assignment to fetch submissions for.

    Returns:
        List[Dict[str, Any]]: A list where each item represents one student’s submission:
            - 'submission_id' (int): The unique Canvas submission ID
            - 'user_id' (int): The Canvas user ID of the student
            - 'user_name' (str): The student’s display name
            - 'submission_type' (str or None): e.g. 'online_quiz', 'online_upload', etc.
            - 'workflow_state' (str): e.g. 'graded', 'submitted', 'unsubmitted'
            - 'grade' (str or None): The letter or numeric grade (if graded)
            - 'score' (float or None): Numeric score (if graded)
            - 'body' (str or None): The submission body (e.g., for online uploads)
            - 'submitted_at' (str or None): Timestamp when submitted (ISO 8601)
            - 'graded_at' (str or None): Timestamp when graded (ISO 8601)
            - 'late' (bool): Whether the submission was late
            - 'missing' (bool): Whether the submission is missing
            - 'preview_url' (str): URL to preview the submission
    Raises:
        Exception: If the API request fails (non-200 status code).

    Notes:
        - Students who have not submitted will appear with workflow_state='unsubmitted'
          and no grade/score.
        - For large classes, consider paginating or filtering via API parameters.
    """
    canvas = get_canvas()
    url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    params = {
        # include additional fields if needed, e.g. include[]=submission_comments
        "include[]": ["user", "submission"],
        "per_page": 100
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(
            f"Error fetching submissions: {response.status_code} - {response.text}"
        )

    raw = response.json()
    formatted = []
    for sub in raw:
        formatted.append({
            "submission_id": sub.get("id"),
            "user_id": sub.get("user_id"),
            "user_name": sub.get("user", {}).get("name"),
            "submission_type": sub.get("submission_type"),
            "workflow_state": sub.get("workflow_state"),
            "grade": sub.get("grade"),
            "score": sub.get("score"),
            "body": sub.get("body"),
            "submitted_at": sub.get("submitted_at"),
            "graded_at": sub.get("graded_at"),
            "late": sub.get("late", False),
            "missing": sub.get("missing", False),
            "preview_url": sub.get("preview_url"),
        })

    return formatted
