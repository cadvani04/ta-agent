from canvasapi import Canvas
import os
import sys
from dotenv import load_dotenv
from discord_agent.discord_openai import create_discord_server, list_discord_channels, read_discord_messages
import canvas_agent.openai_tools as canvas_tools
from agents import Agent, Runner
from canvas_agent.openai_tools import *
from canvas_agent.canvas.canvas_courses import get_all_courses, get_course
from canvas_agent.canvas.canvas_assignments import create_assignment, get_assignments, edit_assignment, delete_assignment
from canvas_agent.canvas.canvas_gradebook_history import get_student_grades
from canvas_agent.canvas.canvas_submissions import get_submissions
from canvas_agent.canvas.canvas_quizzes import create_quiz, list_quizzes, get_quiz, edit_quiz, delete_quiz, reorder_quiz_items, validate_quiz_access_code
from canvas_agent.canvas.canvas_quiz_submissions import list_quiz_submissions, get_quiz_submission, start_quiz_submission, update_quiz_submission, complete_quiz_submission, quiz_submission_time
from canvas_agent.canvas.canvas_quiz_questions import list_quiz_questions, get_quiz_question, create_quiz_question, update_quiz_question, delete_quiz_question
import inspect
from ai_check_agent.ai_checking import check_ai
from slack_agent.slack_agent import monitor_slack_channel, send_slack_message, read_slack_messages, list_slack_channels
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv()

# Get Canvas API URL and token from environment variables
CANVAS_API_URL = os.getenv('CANVAS_API_URL')
CANVAS_API_TOKEN = os.getenv('CANVAS_API_TOKEN')


def make_instructions(course_id: int, discord_server_id: int, discord_channel_id: int, slack_name: str):
    return f"You are an assistant designed to help and assist the user, primarily to help interface and collect insights from different services and APIs. To this end, you have been given some tools pertaining to the Canvas LMS, Discord, and Slack. The Canvas tools allow you to do a multitude of operations that you can do in the actual canvas, and you may interact with the Canvas API given the tools. Based on what you learn from querying the Canvas API, you will give the user information or complete their request in the best fashion that you can. The same goes for the Discord and Slack tools, which will mainly be used to retrieve messages, analyze, and report back to the user in addition to their other capabilities. Your primary course right now is course ID {course_id}. This  means that when unclear or in most cases, you are to respond about this course (unless explicitly asked to provide other information about other courses or data). Based on the user’s query, you may use any combination of the provided tools in any order to complete the task to the maximum possible level. The Discord server ID is {discord_server_id}, and the Discord channel ID is {discord_channel_id}. The Slack is called {slack_name}. You also have a small AI check tool to be used only when specifically asked for."


def main():
    if not CANVAS_API_URL or not CANVAS_API_TOKEN:
        print("Error: CANVAS_API_URL and CANVAS_API_TOKEN must be set in .env file")
        sys.exit(1)

    canvas_tools = [get_all_courses, get_course, create_assignment,
                    get_student_grades, get_assignments, edit_assignment,
                    delete_assignment, get_submissions, create_quiz,
                    list_quizzes, get_quiz, edit_quiz,
                    delete_quiz, reorder_quiz_items, validate_quiz_access_code,
                    list_quiz_submissions, get_quiz_submission, start_quiz_submission,
                    update_quiz_submission, complete_quiz_submission, quiz_submission_time,
                    list_quiz_questions, get_quiz_question, create_quiz_question,
                    update_quiz_question, delete_quiz_question]
    discord_tools = [
        list_discord_channels,
        read_discord_messages,
        create_discord_server
    ]
    slack_tools = [
        list_slack_channels,
        read_slack_messages,
        monitor_slack_channel,
        send_slack_message
    ]
    ai_check_tools = [check_ai]
    all_tools = canvas_tools + discord_tools + ai_check_tools + slack_tools
    # canvas_agent = Agent(name="Canvas Agent",
    #               instructions="You are an assistant designed to help the user interact with the Canvas API. Your primary purpose is to perform actions in the Canvas API given the tools, and give information to the user based on what you can learn from querying the Canvas API and what they ask. Your primary course right now is course ID 11883051. This means that when unclear or in most cases, you are to respond about this course (unless explicitly asked to provide other information about other courses or data).",
    #               model="o4-mini",
    #               tools=canvas_tools)

    # discord_agent = Agent(name="Discord Agent",
    #               instructions="You are an assistant designed to help the user interact with Discord. "
    #                 "You can create new Discord servers, list channels in a server, and read messages. "
    #                 "When the user asks about Discord, use your tools to help them manage their Discord servers."
    #                 "This is the info for CSE 30: DEFAULT_GUILD_ID = 1365757418998464593, DEFAULT_CHANNEL_ID = 1365757421938544721. "
    #                 "This is the info for MATH 19b: DEFAULT_GUILD_ID = 1365763509006372927, DEFAULT_CHANNEL_ID = 1365763511040610365.",
    #                model="o4-mini",
    #                tools=discord_tools)

    master_agent = Agent(name="Master",
                         instructions=make_instructions(
                             11883051, 1365757418998464593, 1365757421938544721, "cse"),
                         model="o4-mini",
                         tools=all_tools)

    user_input = None
    result = None
    while True:
        user_input = input("\n > ")

        if user_input.lower() in ["exit", "quit"]:
            break

        if result is not None:
            user_input = result.to_input_list(
            ) + [{"role": "user", "content": user_input}]

        result = Runner.run_sync(master_agent, user_input)

        print("----\n" + f"{result.final_output}")


if __name__ == "__main__":
    main()
