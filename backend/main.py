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
from canvas_agent.canvas.canvas_assignments import *
from canvas_agent.canvas.canvas_gradebook_history import get_student_grades 
import inspect

# Load environment variables from .env file
load_dotenv()

# Get Canvas API URL and token from environment variables
CANVAS_API_URL = os.getenv('CANVAS_API_URL')
CANVAS_API_TOKEN = os.getenv('CANVAS_API_TOKEN')

def main():
    if not CANVAS_API_URL or not CANVAS_API_TOKEN:
        print("Error: CANVAS_API_URL and CANVAS_API_TOKEN must be set in .env file")
        sys.exit(1)
    
    canvas_tools = [get_all_courses, get_course, create_assignment, 
                 get_student_grades, get_assignments, edit_assignment,
                 delete_assignment]
    discord_tools=[
            list_discord_channels,
            read_discord_messages,
            create_discord_server
        ]
    all_tools = canvas_tools + discord_tools
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
                instructions=(
                   "You are an assistant designed to help the user interact with the Canvas API and Discord API. "
                   "The tools available have been made clear to you. For Discord, This is the info for CSE 30: "
                   "DEFAULT_GUILD_ID = 1365757418998464593, DEFAULT_CHANNEL_ID = 1365757421938544721. This is "
                   "the info for MATH 19b: DEFAULT_GUILD_ID = 1365763509006372927, DEFAULT_CHANNEL_ID = "
                   "1365763511040610365. For Canvas, you may interact with the Canvas API given the tools, "
                   "and give information to the user based on what you can learn from querying the Canvas "
                   "API and what they ask. Your primary course right now is course ID 11883051. This means "
                   "that when unclear or in most cases, you are to respond about this course "
                   "(unless explicitly asked to provide other information about other courses or data). Based "
                   "on the user's query, you may use any combination of the provided tools to complete the task to "
                   "the maximum potential."
                ),
                model="o4-mini",
                tools=all_tools)

    user_input = None
    result = None
    while True:
        user_input = input(" > ")

        if user_input.lower() in ["exit", "quit"]:
            break

        if result is not None:
            user_input = result.to_input_list(
            ) + [{"role": "user", "content": user_input}]

        result = Runner.run_sync(master_agent, user_input)
        
        print("----\n" + f"{result.final_output}")


if __name__ == "__main__":
    main()
