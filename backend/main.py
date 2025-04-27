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
import asyncio
from slack_agent.slack_agent import monitor_slack_channel, send_slack_message, read_slack_messages, list_slack_channels
from openai.types.responses import ResponseTextDeltaEvent
from ai_check_agent.ai_checking import check_ai

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv()

# Get Canvas API URL and token from environment variables
CANVAS_API_URL = os.getenv('CANVAS_API_URL')
CANVAS_API_TOKEN = os.getenv('CANVAS_API_TOKEN')


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
ai_check_tools = [check_ai]
slack_tools = [
    list_slack_channels,
    read_slack_messages,
    monitor_slack_channel,
    send_slack_message
]
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
course_id = 11883051
server_id = 1365757418998464593
channel_id = 1365757421938544721

master_agent = Agent(name="Master",
                     #  instructions=make_instructions(
                     #      course_id, server_id, channel_id),
                     model="gpt-4o-mini",  # "o4-mini",
                     tools=all_tools)

# user_input = None
# result = None
# while True:
#     user_input = input(" > ")

#     if user_input.lower() in ["exit", "quit"]:
#         break

#     if result is not None:
#         user_input = result.to_input_list(
#         ) + [{"role": "user", "content": user_input}]

#     result = Runner.run_sync(master_agent, user_input)

#     print("----\n" + f"{result.final_output}")


@app.get("/list_courses")
def get_all_courses():
    canvas = get_canvas()
    return [{"id": c.id, "name": c.name, "account_id": c.account_id, "root_account_id": c.root_account_id} for c in canvas.get_courses()]


class AgentReq(BaseModel):
    prompt: str


@app.post("/agent")
async def test_run(req: AgentReq):
    result = await Runner.run(master_agent, req.prompt)

    return result.final_output
