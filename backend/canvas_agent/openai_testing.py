from canvasapi import Canvas
import os
import sys
from dotenv import load_dotenv
import openai_tools as canvas_tools
from agents import Agent, Runner
from openai_tools import *
from canvas.canvas_courses import get_all_courses, get_course
from canvas.canvas_assignments import create_assignment, get_assignments, edit_assignment, delete_assignment
from canvas.canvas_gradebook_history import get_student_grades
from canvas.canvas_submissions import get_submissions
from canvas.canvas_quizzes import create_quiz, list_quizzes, get_quiz, edit_quiz, delete_quiz, reorder_quiz_items, validate_quiz_access_code
from canvas.canvas_quiz_submissions import list_quiz_submissions, get_quiz_submission, start_quiz_submission, update_quiz_submission, complete_quiz_submission, quiz_submission_time
from canvas.canvas_quiz_questions import list_quiz_questions, get_quiz_question, create_quiz_question, update_quiz_question, delete_quiz_question
import inspect

# Load environment variables from .env file
load_dotenv()

# Get Canvas API URL and token from environment variables
CANVAS_API_URL = os.getenv('CANVAS_API_URL')
CANVAS_API_TOKEN = os.getenv('CANVAS_API_TOKEN')


def test_fns():
    # Initialize Canvas object
    try:
        canvas = Canvas(CANVAS_API_URL, CANVAS_API_TOKEN)
        print("Successfully connected to Canvas API")
    except Exception as e:
        print(f"Error connecting to Canvas API: {e}")
        sys.exit(1)

    course_id = 11883051  # Replace with a real course ID or mock
    # assignment_id = 54843489  # Replace with a real assignment ID or mock

    # get_quiz_question(course_id, 21774878, 226598323)
    # questions = list_quiz_questions(course_id, 21774878, 0, 0)
    question = QuizQuestionCreate(
        question_name="What's the capital of Spain?",
        question_text="Select the correct answer.",
        question_type="multiple_choice_question",
        points_possible=5,
        answers=[
            {"text": "Madrid", "weight": 100},
            {"text": "Barcelona", "weight": 0},
            {"text": "Seville", "weight": 0}
        ]
    )

    created = create_quiz_question(
        course_id=course_id, quiz_id=21774878, question_data=question)
    print(created)
    # print(questions)
    exit()


def main():
    if not CANVAS_API_URL or not CANVAS_API_TOKEN:
        print("Error: CANVAS_API_URL and CANVAS_API_TOKEN must be set in .env file")
        sys.exit(1)
    # test_fns()
    tool_list = [get_all_courses, get_course, create_assignment,
                 get_student_grades, get_assignments, edit_assignment,
                 delete_assignment, get_submissions, create_quiz,
                 list_quizzes, get_quiz, edit_quiz,
                 delete_quiz, reorder_quiz_items, validate_quiz_access_code,
                 list_quiz_submissions, get_quiz_submission, start_quiz_submission,
                 update_quiz_submission, complete_quiz_submission, quiz_submission_time,
                 list_quiz_questions, get_quiz_question, create_quiz_question,
                 update_quiz_question, delete_quiz_question]

    agent = Agent(name="Canvas Agent",
                  instructions="You are an assistant designed to help the user interact with the Canvas API. Your primary purpose is to perform actions in the Canvas API given the tools, and give information to the user based on what you can learn from querying the Canvas API and what they ask. Your primary course right now is course ID 11883051. This means that when unclear or in most cases, you are to respond about this course (unless explicitly asked to provide other information about other courses or data).",
                  model="gpt-4o-mini",
                  tools=tool_list)

    user_input = None
    result = None
    while True:
        user_input = input(" > ")

        if user_input.lower() in ["exit", "quit"]:
            break

        if result is not None:
            user_input = result.to_input_list(
            ) + [{"role": "user", "content": user_input}]

        result = Runner.run_sync(agent, user_input)

        print("----\n" + f"{result.final_output}")


if __name__ == "__main__":
    main()
