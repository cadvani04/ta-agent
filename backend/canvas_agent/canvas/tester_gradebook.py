import os
import sys
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
from typing import Optional, List, Dict, Any

# Import the gradebook functions
from canvas_gradebook_history import (
    get_student_enrollments_with_grades,
    get_grade_history_for_course,
    get_grade_history_for_assignment,
    get_grade_history_for_student
)

# Load environment variables
load_dotenv()
CANVAS_API_TOKEN = os.getenv('canvas_token')
CANVAS_API_URL = os.getenv('CANVAS_API_URL', 'https://canvas.instructure.com')

# Default course ID for testing
DEFAULT_COURSE_ID = 11883051  # Replace with your actual course ID

async def test_student_enrollments():
    print("\n=== Testing Student Enrollments with Grades ===")
    course_id = DEFAULT_COURSE_ID
    print(f"Using course ID: {course_id}")
    
    try:
        enrollments = await get_student_enrollments_with_grades(course_id)
        
        print(f"Found {len(enrollments)} student enrollments")
        if enrollments:
            print("\nSample student data:")
            for enrollment in enrollments[:3]:  # Show first 3 for brevity
                print(f"Student: {enrollment['user']['name']}")
                print(f"Current Grade: {enrollment['grades'].get('current_grade', 'N/A')}")
                print(f"Final Score: {enrollment['grades'].get('final_score', 'N/A')}")
                print("---")
            
            # Return the first user ID for further tests
            return enrollments[0]['user_id'] if enrollments else None
        else:
            print("No enrollments found")
            return None
    except Exception as e:
        print(f"Error fetching enrollments: {e}")
        return None

async def test_grade_history(assignment_id=None):
    print("\n=== Testing Grade History for Course ===")
    course_id = DEFAULT_COURSE_ID
    print(f"Using course ID: {course_id}")
    
    try:
        history = await get_grade_history_for_course(course_id)
        
        print(f"Found {len(history)} grade history events")
        if history:
            print("\nSample grade history events:")
            for event in history[:3]:  # Show first 3 for brevity
                print(f"Assignment: {event.get('assignment_name', 'N/A')}")
                print(f"Student: {event.get('student_name', 'N/A')}")
                print(f"Grader: {event.get('grader_name', 'N/A')}")
                print(f"Grade: {event.get('current_grade', 'N/A')}")
                print("---")
            
            # Return the first assignment ID for further tests
            if not assignment_id and history:
                return history[0].get('assignment_id')
        else:
            print("No grade history events found")
        
        return assignment_id
    except Exception as e:
        print(f"Error fetching grade history: {e}")
        return assignment_id

async def test_assignment_grade_history(assignment_id, user_id=None):
    if not assignment_id:
        print("No assignment ID available. Skipping assignment grade history test.")
        return
    
    print(f"\n=== Testing Grade History for Assignment {assignment_id} ===")
    course_id = DEFAULT_COURSE_ID
    print(f"Using course ID: {course_id}")
    
    try:
        history = await get_grade_history_for_assignment(course_id, assignment_id)
        
        print(f"Found {len(history)} grade history events for assignment")
        if history:
            print("\nSample grade history events:")
            for event in history[:3]:  # Show first 3 for brevity
                print(f"Student: {event.get('user_name', 'N/A')}")
                print(f"Grade: {event.get('current_grade', 'N/A')}")
                print(f"Graded at: {event.get('graded_at', 'N/A')}")
                print("---")
            
            # Return the first user ID for further tests
            if not user_id and history:
                return history[0].get('user_id')
        else:
            print("No grade history events found for this assignment")
        
        return user_id
    except Exception as e:
        print(f"Error fetching assignment grade history: {e}")
        return user_id

async def test_student_grade_history(assignment_id, user_id):
    if not assignment_id or not user_id:
        print("Missing assignment ID or user ID. Skipping student grade history test.")
        return
    
    print(f"\n=== Testing Grade History for Student {user_id} on Assignment {assignment_id} ===")
    course_id = DEFAULT_COURSE_ID
    print(f"Using course ID: {course_id}")
    
    try:
        history = await get_grade_history_for_student(course_id, assignment_id, user_id)
        
        print(f"Found {len(history)} grade history events for student on assignment")
        if history:
            print("\nGrade history events:")
            for event in history:
                print(f"Grade: {event.get('current_grade', 'N/A')}")
                print(f"Graded at: {event.get('graded_at', 'N/A')}")
                print(f"Grader: {event.get('grader', 'N/A')}")
                print("---")
        else:
            print("No grade history events found for this student on this assignment")
    except Exception as e:
        print(f"Error fetching student grade history: {e}")

async def interactive_session():
    print("\n=== Interactive Canvas Gradebook Agent Session ===")
    print("Type 'exit' or 'quit' to end the session")
    
    agent = Agent(
        name="canvas-gradebook-agent",
        instructions=(
            "You are an assistant designed to help the user access and understand Canvas gradebook data. "
            "You can retrieve student enrollments with grades, view grade history for courses, "
            "assignments, and individual students. When the user asks about grades or gradebook "
            "information, use your tools to provide the relevant data."
            f"The default course ID for testing is {DEFAULT_COURSE_ID}."
        ),
        tools=[
            get_student_enrollments_with_grades,
            get_grade_history_for_course,
            get_grade_history_for_assignment,
            get_grade_history_for_student
        ],
        model="gpt-4o-mini",
    )

    user_input = None
    result = None
    
    while True:
        user_input = input(" > ")

        if user_input.lower() in ["exit", "quit"]:
            break

        if result is not None:
            user_input = result.to_input_list() + [{"role": "user", "content": user_input}]

        result = await Runner.run(agent, user_input)
        print("Agent response: ", result.final_output)

async def main():
    # Check if Canvas token is set
    if not CANVAS_API_TOKEN:
        print("Error: canvas_token must be set in .env file")
        sys.exit(1)

    print(f"Using Canvas API URL: {CANVAS_API_URL}")
    print(f"Using Canvas token: {CANVAS_API_TOKEN[:10]}...")

    # Run automated tests
    print("\n--- Running Automated Tests ---")
    user_id = await test_student_enrollments()
    assignment_id = await test_grade_history()
    user_id = await test_assignment_grade_history(assignment_id, user_id)
    await test_student_grade_history(assignment_id, user_id)
    
    # Run interactive session
    await interactive_session()

if __name__ == "__main__":
    asyncio.run(main()) 