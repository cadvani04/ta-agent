""" *** this is where we see grades and stuff
List enrollments**
Enrollment by ID**
Enroll a user**
Conclude, deactivate, or delete an enrollment
Accept Course Invitation
Reject Course Invitation
Re-activate an enrollment
Add last attended date
Show Temporary Enrollment recipient and provider status
"""
from openai_tools import *


# NOT USING!!
@function_tool()
def get_grades(course_id: str):
    """
    Gets grades for students in a specified course, returning a list of dictionaries with user_id and current_grade fields.

    Args:
        course_id (str): The ID of the course to retrieve enrollment data for.

    Returns:
        list: A list of dictionaries, each containing:
            - user_id (int): The ID of the student.
            - current_grade (str or None): The current grade for the student out of 100, or null if unavailable.

    Raises:
        HTTPException: If there's an API error or the course ID is invalid.
    """
    canvas = get_canvas()   
    enrollments = canvas.get_course(course_id).get_enrollments(type=['StudentEnrollment'])
    results = []
    for enrollment in enrollments:
        if hasattr(enrollment, "grades"):
            grades = enrollment.grades
            print(enrollment.user_name)
            results.append({
                'user_id': enrollment.user_id,
                'current_grade': grades.get('current_score'),
            })
    
    return results