import os
import sys
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from openai.types.responses import ResponseTextDeltaEvent

from agents import Agent, Runner
from slack_agent.slack_agent import monitor_slack_channel, send_slack_message, read_slack_messages, list_slack_channels
from ai_check_agent.ai_checking import check_ai
from discord_agent.discord_openai import create_discord_server, list_discord_channels, read_discord_messages
from canvas_agent.canvas.canvas_quiz_questions import (
    list_quiz_questions, get_quiz_question,
    create_quiz_question, update_quiz_question, delete_quiz_question
)
from canvas_agent.canvas.canvas_quiz_submissions import (
    list_quiz_submissions, get_quiz_submission,
    start_quiz_submission, update_quiz_submission,
    complete_quiz_submission, quiz_submission_time
)
from canvas_agent.canvas.canvas_quizzes import (
    create_quiz, list_quizzes, get_quiz,
    edit_quiz, delete_quiz, reorder_quiz_items,
    validate_quiz_access_code
)
from canvas_agent.canvas.canvas_submissions import get_submissions
from canvas_agent.canvas.canvas_gradebook_history import get_student_grades
from canvas_agent.canvas.canvas_assignments import create_assignment, get_assignments, edit_assignment, delete_assignment
from canvas_agent.canvas.canvas_courses import get_all_courses, get_course

# helper to isolate agent on its own loop in a thread


def _run_agent_with_new_loop(agent, conversation):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return Runner.run_sync(agent, conversation)


# add backend dir if needed
backend_dir = Path(__file__).parent / "backend"
sys.path.append(str(backend_dir))

# load env
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory=".")


def make_instructions(course_id: int, discord_server_id: int, discord_channel_id: int, slack_name: str):
    #return f"You are an assistant designed to help and assist the user, primarily to help interface and collect insights from different services and APIs. To this end, you have been given some tools pertaining to the Canvas LMS, Discord, and Slack. The Canvas tools allow you to do a multitude of operations that you can do in the actual canvas, and you may interact with the Canvas API given the tools. Based on what you learn from querying the Canvas API, you will give the user information or complete their request in the best fashion that you can. The same goes for the Discord and Slack tools, which will mainly be used to retrieve messages, analyze, and report back to the user in addition to their other capabilities. When you reference a course, make sure it's right, and when you speak to the user, make sure you mention the course name and not the ID.  Your primary course right now is course ID {course_id}. This  means that when unclear or in most cases, you are to respond about this course (unless explicitly asked to provide other information about other courses or data). Based on the user’s query, you may use any combination of the provided tools in any order to complete the task to the maximum possible level. The Discord server ID is {discord_server_id}, and the Discord channel ID is {discord_channel_id}. The Slack is called {slack_name}. You also have a small AI check tool to be used only when specifically asked for. "
    return f"You are an assistant designed to help and assist the user, primarily to help interface and collect insights from different services and APIs. To this end, you have been given some tools pertaining to the Canvas LMS, Discord, and Slack. The Canvas tools allow you to do a multitude of operations that you can do in the actual canvas, and you may interact with the Canvas API given the tools. Based on what you learn from querying the Canvas API, you will give the user information or complete their request in the best fashion that you can. The same goes for the Discord and Slack tools, which will mainly be used to retrieve messages, analyze, and report back to the user in addition to their other capabilities. When you reference a course, make sure it's right, and when you speak to the user, make sure you mention the course name and not the ID.  Your primary course right now is course ID {course_id}. This  means that when unclear or in most cases, you are to respond about this course (unless explicitly asked to provide other information about other courses or data). Based on the user's query, you may use any combination of the provided tools in any order to complete the task to the maximum possible level. The Discord server ID is {discord_server_id}, and the Discord channel ID is {discord_channel_id}. The Slack is called {slack_name}. You also have a small AI check tool to be used only when specifically asked for. When sending messages on Discord or Slack, you must sound like a real human TA - avoid template-like responses, use casual language, occasionally include minor typos, vary your greeting styles, and match the conversational tone of students. Your responses should feel natural and personable, as if coming from an actual teaching assistant rather than an AI system."

def get_master_agent(course_id, discord_server_id, discord_channel_id, slack_name):
    # gather tools
    canvas_tools = [
        get_all_courses, get_course,
        create_assignment, get_assignments, edit_assignment, delete_assignment,
        get_submissions,
        create_quiz, list_quizzes, get_quiz, edit_quiz, delete_quiz,
        reorder_quiz_items, validate_quiz_access_code,
        list_quiz_submissions, get_quiz_submission, start_quiz_submission,
        update_quiz_submission, complete_quiz_submission, quiz_submission_time,
        list_quiz_questions, get_quiz_question, create_quiz_question,
        update_quiz_question, delete_quiz_question
    ]
    discord_tools = [list_discord_channels,
                     read_discord_messages, create_discord_server]
    slack_tools = [list_slack_channels, read_slack_messages,
                   monitor_slack_channel, send_slack_message]
    ai_tools = [check_ai]
    all_tools = canvas_tools + discord_tools + slack_tools + ai_tools

    return Agent(
        name="Master",
        instructions=make_instructions(
            course_id, discord_server_id, discord_channel_id, slack_name),
        model="o4-mini",
        tools=all_tools
    )


@app.get("/", response_class=HTMLResponse)
async def get_root(request: Request):
    return templates.TemplateResponse("ta_chat.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # default context = MATH 19B
    master_agent = get_master_agent(
        11883045, 1365763509006372927, 1365763511040610365, "math"
    )
    conversation = []

    while True:
        raw = await websocket.receive_text()

        # is this our switch command?
        try:
            data = json.loads(raw)
        except ValueError:
            data = None

        if data and data.get("type") == "switch":
            # rebuild agent + clear convo
            master_agent = get_master_agent(
                int(data["course_id"]),
                int(data["discord_server_id"]),
                int(data["discord_channel_id"]),
                data["slack_name"]
            )
            conversation = []

            # send exactly one switch-ack
            await websocket.send_json({
                "type": "response",
                "content": f"Switched to {data['course_name']}. How can I assist you?"
            })
            continue

        # normal user message → agent
        user_input = conversation + \
            [{"role": "user", "content": raw}] if conversation else raw

        await websocket.send_json({"type": "thinking", "content": "Processing..."})

        result = Runner.run_streamed(master_agent, user_input)

        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)

        # result = await asyncio.to_thread(_run_agent_with_new_loop, master_agent, user_input)
        conversation = result.to_input_list()
        await websocket.send_json({"type": "response", "content": result.final_output})

if __name__ == "__main__":
    print("Starting TA Agent chat server on http://localhost:8004")
    uvicorn.run(app, host="0.0.0.0", port=8004)
