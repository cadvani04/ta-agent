"""
Canvas Gradebook History API

This module provides functions to interact with the Canvas Gradebook History API.
https://canvas.instructure.com/doc/api/gradebook_history.html

It includes functionality to:
- Get student enrollments with grades
- Get gradebook history for a course
- Get grade change events
"""

import os
import requests
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from canvasapi import Canvas
from agents import function_tool

# Load environment variables
load_dotenv()
CANVAS_API_URL = os.getenv('CANVAS_API_URL', 'https://canvas.instructure.com')
CANVAS_API_TOKEN = os.getenv('canvas_token')

def get_canvas():
    """Get a Canvas API client instance."""
    if not CANVAS_API_TOKEN:
        raise ValueError("Canvas API token not found in environment variables")
    return Canvas(CANVAS_API_URL, CANVAS_API_TOKEN)

class GradeData(BaseModel):
    """Model for student grade data."""
    html_url: str
    current_grade: Optional[str] = None
    current_score: Optional[float] = None
    final_grade: Optional[str] = None
    final_score: Optional[float] = None
    unposted_current_grade: Optional[str] = None
    unposted_current_score: Optional[float] = None
    unposted_final_grade: Optional[str] = None
    unposted_final_score: Optional[float] = None

class EnrollmentWithGrades(BaseModel):
    """Model for enrollment data with grades."""
    id: int
    user_id: int
    course_id: int
    type: str
    role: str
    role_id: int
    user: Dict[str, Any]
    grades: GradeData

@function_tool()
def get_student_enrollments_with_grades(course_id: int) -> List[Dict[str, Any]]:
    """
    Get student enrollments with grades for a specific course.
    
    Args:
        course_id (int): The Canvas course ID
        
    Returns:
        List[Dict[str, Any]]: A list of student enrollments with grade information
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
            "sortable_name": enrollment["user"].get("sortable_name", ""),
            "short_name": enrollment["user"].get("short_name", "")
        }
        
        # Extract grade information
        grades = enrollment.get("grades", {})
        
        formatted_enrollment = {
            "id": enrollment["id"],
            "user_id": enrollment["user_id"],
            "course_id": enrollment["course_id"],
            "type": enrollment["type"],
            "role": enrollment["role"],
            "user": user_info,
            "grades": {
                "current_grade": grades.get("current_grade"),
                "current_score": grades.get("current_score"),
                "final_grade": grades.get("final_grade"),
                "final_score": grades.get("final_score"),
                "unposted_current_grade": grades.get("unposted_current_grade"),
                "unposted_current_score": grades.get("unposted_current_score"),
                "unposted_final_grade": grades.get("unposted_final_grade"),
                "unposted_final_score": grades.get("unposted_final_score")
            }
        }
        
        formatted_enrollments.append(formatted_enrollment)
        print(formatted_enrollment)
    
    return formatted_enrollments

@function_tool()
def get_grade_history_for_course(course_id: int) -> List[Dict[str, Any]]:
    """
    Get the grade change history for a course.
    
    Args:
        course_id (int): The Canvas course ID
        
    Returns:
        List[Dict[str, Any]]: A list of grade change events
    """
    canvas = get_canvas()
    
    url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/gradebook_history/feed"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching grade history: {response.status_code} - {response.text}")
    
    print(response.json())
    return response.json()

@function_tool()
def get_grade_history_for_assignment(course_id: int, assignment_id: int) -> List[Dict[str, Any]]:
    """
    Get the grade change history for a specific assignment.
    
    Args:
        course_id (int): The Canvas course ID
        assignment_id (int): The Canvas assignment ID
        
    Returns:
        List[Dict[str, Any]]: A list of grade change events for the assignment
    """
    canvas = get_canvas()
    
    url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/gradebook_history/{assignment_id}"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching assignment grade history: {response.status_code} - {response.text}")
    
    print(response.json())
    return response.json()

@function_tool()
def get_grade_history_for_student(course_id: int, assignment_id: int, user_id: int) -> List[Dict[str, Any]]:
    """
    Get the grade change history for a specific student on a specific assignment.
    
    Args:
        course_id (int): The Canvas course ID
        assignment_id (int): The Canvas assignment ID
        user_id (int): The Canvas user ID
        
    Returns:
        List[Dict[str, Any]]: A list of grade change events for the student on the assignment
    """
    canvas = get_canvas()
    
    url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/gradebook_history/{assignment_id}/{user_id}"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching student grade history: {response.status_code} - {response.text}")
    
    print(response.json())
    return response.json()

@function_tool()
def get_grade_history_details(course_id: int, assignment_id: int, user_id: int, version_id: int) -> Dict[str, Any]:
    """
    Get the details of a specific grade change event.
    
    Args:
        course_id (int): The Canvas course ID
        assignment_id (int): The Canvas assignment ID
        user_id (int): The Canvas user ID
        version_id (int): The version ID of the grade change
        
    Returns:
        Dict[str, Any]: Details of the grade change event
    """
    canvas = get_canvas()
    
    url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/gradebook_history/{assignment_id}/{user_id}/{version_id}"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching grade history details: {response.status_code} - {response.text}")
    
    print(response.json())
    return response.json()

'''
# Example usage
if __name__ == "__main__":
    # Replace with an actual course ID
    test_course_id = 11883051
    
    try:
        print("Fetching student enrollments with grades...")
        enrollments = get_student_enrollments_with_grades(test_course_id)
        
        print(f"Found {len(enrollments)} student enrollments")
        for enrollment in enrollments[:3]:  # Print first 3 for brevity
            print(f"Student: {enrollment['user']['name']}")
            print(f"Current Grade: {enrollment['grades']['current_grade']}")
            print(f"Final Score: {enrollment['grades']['final_score']}")
            print("---")
            
    except Exception as e:
        print(f"Error: {e}")
'''