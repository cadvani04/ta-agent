"""
Canvas Gradebook History API

This module provides functions to interact with the Canvas Gradebook History API.
https://canvas.instructure.com/doc/api/gradebook_history.html
"""
from canvas_agent.openai_tools import *


# not being used rly
@function_tool()
def get_grade_history_for_course(course_id: int) -> List[Dict[str, Any]]:
    """
    Fetch the full grade change history for a specific course.

    This function queries the Canvas API to retrieve all recorded grade change 
    events in a course's gradebook. Each event contains information such as 
    who changed a grade, which student's grade was affected, what the old 
    and new grades were, and when the change occurred.

    Args:
        course_id (int): The Canvas course ID to retrieve grade history from.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a 
        grade change event. Fields in each event may include:
            - 'user_id': ID of the student whose grade was changed
            - 'grader_id': ID of the person who changed the grade
            - 'assignment_id': ID of the assignment whose grade changed
            - 'grade_before' / 'grade_after': Old and new grades
            - 'graded_at': Timestamp of when the grade change occurred
            - Other metadata related to the grade change

    Raises:
        Exception: If the API request fails (non-200 status code).

    Note:
        - This will only return grade changes that are *recorded* by Canvas.
        - If no grades were changed, the returned list will be empty.
    """
    canvas = get_canvas()

    url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/gradebook_history/feed"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Error fetching grade history: {response.status_code} - {response.text}")

    return response.json()


@function_tool()
def get_student_grades(course_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve the current grades for all active students in a specific course.

    This function queries the Canvas API to get a list of all active student enrollments 
    in a course, along with each student's current grade and score. 
    It organizes the returned data into a clean, structured format, including 
    the student's name, user ID, and grade details.

    Args:
        course_id (int): The Canvas course ID from which to fetch student grades.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, one per student, each containing:
            - 'user_id': The Canvas user ID of the student
            - 'user': A dictionary with:
                - 'id': User ID (redundant but available)
                - 'name': Full name of the student
            - 'grades': A dictionary with:
                - 'current_grade': The student's current letter grade (e.g., "B+")
                - 'current_score': The student's current percentage score (e.g., 88.5)

    Raises:
        Exception: If the API request fails (non-200 status code).

    Note:
        - Only active enrollments (not dropped or inactive students) are included.
        - If a student does not have a grade yet, 'current_grade' and 'current_score' may be null.
    """
    canvas = get_canvas()

    # Direct API request to include grades
    url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/enrollments"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    params = {
        "type[]": "StudentEnrollment",
        "state[]": "active",
        "include[]": "grades"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Error fetching enrollments: {response.status_code} - {response.text}")

    enrollments = response.json()

    # Process and format the enrollment data
    formatted_enrollments = []
    for enrollment in enrollments:
        # Extract relevant user information
        user_info = {
            "id": enrollment["user"]["id"],
            "name": enrollment["user"]["name"],
        }
        # Extract grade information
        grades = enrollment.get("grades", {})
        formatted_enrollment = {
            "user_id": enrollment["user_id"],
            "user": user_info,
            "grades": {
                "current_grade": grades.get("current_grade"),
                "current_score": grades.get("current_score"),
            }
        }
        formatted_enrollments.append(formatted_enrollment)
    return formatted_enrollments


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
            "submitted_at": sub.get("submitted_at"),
            "graded_at": sub.get("graded_at"),
            "late": sub.get("late", False),
            "missing": sub.get("missing", False),
            "preview_url": sub.get("preview_url"),
        })

    return formatted
