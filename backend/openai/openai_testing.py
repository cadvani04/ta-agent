from canvasapi import Canvas
import os
import sys
from dotenv import load_dotenv
import openai_tools as canvas_tools
from agents import Agent, Runner
from openai_tools import *
from canvas.canvas_courses import *
from canvas.canvas_assignments import *
from canvas.canvas_accounts import *
from canvas.canvas_gradebook_history import *
import inspect

# Load environment variables from .env file
load_dotenv()

# Get Canvas API URL and token from environment variables
CANVAS_API_URL = os.getenv('CANVAS_API_URL')
CANVAS_API_TOKEN = os.getenv('CANVAS_API_TOKEN')
print(CANVAS_API_URL)
print(CANVAS_API_TOKEN)

def test_fns():
    # Initialize Canvas object
    try:
        canvas = Canvas(CANVAS_API_URL, CANVAS_API_TOKEN)
        print("Successfully connected to Canvas API")
    except Exception as e:
        print(f"Error connecting to Canvas API: {e}")
        sys.exit(1)

    # Test 1: Get all courses
    # try:
    #     print("\n--- Test 1: Get All Courses ---")
    #     courses_info = canvas_tools.get_all_courses()
    #     print(courses_info)
    # except Exception as e:
    #     print(f"Error getting courses: {e}")
    # try:
    #     print("\n--- Testing getting the account---")
    #     account = canvas.get_account(0)
    #     print(account.id)
        
    #     # print([{"id": acc.id, "name": acc.name} for acc in accounts])
    #     # print(courses_info)
    # except Exception as e:
    #     print(f"Error getting courses: {e}")
    # # Test 2: Get course users (if courses exist)
    # try:
    #     print("\n--- Test 2: Get Course Users ---")
    #     # Get the first course ID (if available)
    #     courses = list(canvas.get_courses())
    #     if courses:
    #         course_id = courses[0].id
    #         print(f"Getting users for course ID: {course_id}")
    #         users = canvas_tools.get_course_users(course_id)
    #         for user in users:
    #             print(
    #                 f"User ID: {user.id}, Name: {user.name}, Email: {getattr(user, 'email', 'N/A')}")
    #     else:
    #         print("No courses available to test get_course_users")
    # except Exception as e:
    #     print(f"Error getting course users: {e}")

    # # Test 3: Get course assignments (if courses exist)
    # try:
    #     print("\n--- Test 3: Get Course Assignments ---")
    #     # Get the first course ID (if available)
    #     if courses:
    #         course_id = courses[0].id
    #         print(f"Getting assignments for course ID: {course_id}")
    #         assignments = canvas_tools.list_assignments(course_id)
    #         for assignment in assignments:
    #             print(
    #                 f"Assignment ID: {assignment.id}, Name: {assignment.name}")
    #     else:
    #         print("No courses available to test get_course_assignments")
    # except Exception as e:
    #     print(f"Error getting course assignments: {e}")

    # # Test 4: Create and delete an assignment (if courses exist)
    # try:
    #     print("\n--- Test 4: Create and Delete Assignment ---")
    #     if courses:
    #         course_id = courses[0].id
    #         print(f"Creating test assignment in course ID: {course_id}")

    #         # Create a test assignment payload
    #         assignment_data = {
    #             "course_id": course_id,
    #             "assignment_name": "Test Assignment (API Test)",
    #             "description": "This is a test assignment created via the Canvas API",
    #             "points_possible": 10
    #         }

    #         print(
    #             f"Created assignment: ID: {assignment['id']}, Name: {assignment['name']}")

    #         # Delete the test assignment
    #         print(f"Deleting test assignment ID: {assignment['id']}")
    #         result = canvas_tools.delete_assignment(
    #             course_id=course_id, assignment_id=assignment["id"])
    #         print(f"Assignment deleted: {result}")
    #     else:
    #         print("No courses available to test create/delete assignment")
    # except Exception as e:
    #     print(f"Error in assignment creation/deletion test: {e}")
    get_users(81259)
    exit()
    # run an interactive session

def main():
    if not CANVAS_API_URL or not CANVAS_API_TOKEN:
        print("Error: CANVAS_API_URL and CANVAS_API_TOKEN must be set in .env file")
        sys.exit(1)
    test_fns()
    tool_list = [get_all_courses, get_course, create_assignment, get_grade_history_for_course, get_grade_history_for_assignment, get_grade_history_for_student]

    agent = Agent(name="Canvas Agent",
                  instructions="You are an assistant designed to help the user interact with the Canvas API. Your primary purpose is to perform actions in the Canvas API given the tools, and give information to the user based on what you can learn from querying the Canvas API and what they ask.",
                  model="gpt-4o-mini",
                  tools=tool_list)

    user_input = None
    result = None
    while True:
        user_input = input(" >")

        if user_input.lower() in ["exit", "quit"]:
            break

        if result is not None:
            user_input = result.to_input_list(
            ) + [{"role": "user", "content": user_input}]

        result = Runner.run_sync(agent, user_input)
        print("model response: ", result.final_output)


if __name__ == "__main__":
    main()
