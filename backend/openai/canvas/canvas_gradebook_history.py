"""
Canvas Gradebook History API

This module provides functions to interact with the Canvas Gradebook History API.
https://canvas.instructure.com/doc/api/gradebook_history.html
"""
from openai_tools import *


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
        raise Exception(f"Error fetching grade history: {response.status_code} - {response.text}")
    
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
        raise Exception(f"Error fetching enrollments: {response.status_code} - {response.text}")
    
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

# @function_tool()
# def get_grade_history_for_assignment(course_id: int, assignment_id: int) -> List[Dict[str, Any]]:
#     """
#     Get the grade change history for a specific assignment.
    
#     Args:
#         course_id (int): The Canvas course ID
#         assignment_id (int): The Canvas assignment ID
        
#     Returns:
#         List[Dict[str, Any]]: A list of grade change events for the assignment
#     """
#     canvas = get_canvas()
    
#     url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/gradebook_history/{assignment_id}"
#     headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    
#     response = requests.get(url, headers=headers)
    
#     if response.status_code != 200:
#         raise Exception(f"Error fetching assignment grade history: {response.status_code} - {response.text}")
    
#     print(response.json())
#     return response.json()