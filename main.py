import os
import sys
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

# Add necessary paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend/openai/canvas'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend/Discord'))

# Import Canvas Groups functions
from canvas_groups import (
    list_groups_in_context,
    get_group,
    create_group,
    list_group_users,
    add_user_to_group,
    get_group_activity_stream
)

# Import Discord functionality
from discord_agent import create_canvas_discord_agent, client

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('discord_token')
CANVAS_API_TOKEN = os.getenv('canvas_token')

def create_canvas_agent():
    """Create a Canvas Groups agent."""
    return Agent(
        name="canvas-groups-agent",
        instructions=(
            "You are an assistant that helps manage Canvas groups. "
            "You can list groups in a course, get group details, create groups, "
            "list users in a group, add users to groups, and get group activity streams."
        ),
        tools=[
            list_groups_in_context,
            get_group,
            create_group,
            list_group_users,
            add_user_to_group,
            get_group_activity_stream
        ],
        model="gpt-4o-mini",
    )

async def interactive_session(agent):
    """Run an interactive session with the agent."""
    print("\n=== Interactive Agent Session ===")
    print("Type 'exit' or 'quit' to end the session")
    
    result = None
    while True:
        user_input = input(" > ")
        
        if user_input.lower() in ["exit", "quit"]:
            break
        
        # For the first query, just use the query text
        # For subsequent queries, include the conversation history
        if result is None:
            input_data = user_input
        else:
            input_data = result.to_input_list() + [{"role": "user", "content": user_input}]
        
        # Run the agent
        result = await Runner.run(agent, input_data)
        
        # Print the result
        print(f"Agent: {result.final_output}")

async def run_interactive_test():
    """Run an interactive test of the Canvas Groups agent."""
    # Create the agent
    agent = create_canvas_agent()
    
    # Run interactive session
    await interactive_session(agent)

def run_discord_bot():
    """Run the Discord bot with Canvas Groups functionality."""
    # Check if Discord token is set
    if not DISCORD_TOKEN:
        print("Error: discord_token must be set in .env file")
        return
    
    print(f"Starting Discord bot...")
    # Run the Discord client
    client.run(DISCORD_TOKEN)

def main():
    """Main function to run the application."""
    # Check if Canvas token is set
    if not CANVAS_API_TOKEN:
        print("Warning: canvas_token is not set in .env file. Canvas functionality will not work.")
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Run the Canvas Discord Agent')
    parser.add_argument('--mode', choices=['interactive', 'discord', 'test'], default='interactive',
                      help='Mode to run the agent in (interactive, discord, or test)')
    args = parser.parse_args()
    
    print(f"Running in {args.mode} mode")
    
    # Run in the specified mode
    if args.mode == 'interactive':
        asyncio.run(run_interactive_test())
    elif args.mode == 'discord':
        run_discord_bot()
    elif args.mode == 'test':
        # Run a simple test of the Canvas Groups functions
        from canvas_groups import list_groups_in_context, create_group
        
        # Test listing groups
        print("Testing list_groups_in_context...")
        groups = list_groups_in_context('course', 11883051)
        print(f"Found {len(groups)} groups")
        
        # Test creating a group
        if len(groups) == 0:
            print("Testing create_group...")
            import time
            group_name = f"Test Group {int(time.time())}"
            new_group = create_group(
                name=group_name,
                description="A test group created via API",
                join_level="invitation_only",
                is_public=False,
                context_type="course",
                context_id=11883051
            )
            print(f"Created group: {new_group.get('name', 'Unknown')}")

if __name__ == "__main__":
    main() 