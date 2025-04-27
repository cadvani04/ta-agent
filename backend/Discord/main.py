import os
import sys
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner

# Add necessary paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Discord functionality
from Discord.discord_openai import (
    list_discord_channels,
    read_discord_messages,
    create_discord_server
)

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('discord_token')

# Default server IDs
CSE30_GUILD_ID = "1365757418998464593"
CSE30_CHANNEL_ID = "1365757421938544721"
MATH19B_GUILD_ID = "1365763509006372927"
MATH19B_CHANNEL_ID = "1365763511040610365"

def create_discord_agent():
    """Create a Discord agent."""
    return Agent(
        name="discord-agent",
        instructions=(
            "You are an assistant designed to help with Discord. "
            "You can create servers, list channels, and read messages. "
            f"CSE 30 server ID: {CSE30_GUILD_ID}, channel ID: {CSE30_CHANNEL_ID}. "
            f"MATH 19b server ID: {MATH19B_GUILD_ID}, channel ID: {MATH19B_CHANNEL_ID}."
        ),
        tools=[
            list_discord_channels,
            read_discord_messages,
            create_discord_server
        ],
        model="gpt-4o-mini",
    )

async def chat_with_agent():
    """Simple chat interface with the Discord agent."""
    agent = create_discord_agent()
    print("\n=== Discord Agent Chat ===")
    print("Type 'exit' or 'quit' to end the chat")
    
    conversation = []
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ["exit", "quit"]:
            break
        
        # Add user message to conversation
        conversation.append({"role": "user", "content": user_input})
        
        # Run the agent
        result = await Runner.run(agent, conversation)
        
        # Print the result
        print(f"\nAgent: {result.final_output}")
        
        # Add agent response to conversation
        conversation.append({"role": "assistant", "content": result.final_output})

if __name__ == "__main__":
    asyncio.run(chat_with_agent())