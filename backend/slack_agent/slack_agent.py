import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from agents import function_tool, Agent, Runner

# Load environment variables
load_dotenv()
SLACK_TOKEN_MATH = os.getenv('SLACK_BOT_MATH')
SLACK_TOKEN_CSE = os.getenv('SLACK_BOT_CSE')

if not SLACK_TOKEN_MATH:
    raise ValueError("SLACK_BOT_MATH environment variable is not set")
if not SLACK_TOKEN_CSE:
    print("Warning: SLACK_BOT_CSE environment variable is not set")

# Define core functions that will be used for both direct calls and as function tools
@function_tool()
def list_slack_channels(course: str) -> List[Dict[str, Any]]:
    """
    List all channels in a Slack workspace.
    
    Args:
        course (str): Which course to use ("math" or "cse")
        
    Returns:
        List[Dict[str, Any]]: A list of channel objects with id, name, and is_private
    """
    # Handle default value inside the function
    if not course or course.lower() not in ["math", "cse"]:
        course = "math"
    
    # Determine which token to use
    token = SLACK_TOKEN_MATH if course.lower() == "math" else SLACK_TOKEN_CSE
    
    # Create a Slack client
    client = WebClient(token=token)
    
    print(f"Listing channels in {course} workspace")
    
    # Get the list of channels
    response = client.conversations_list(types="public_channel,private_channel")
    channels = response["channels"]
    
    # Format the channels
    formatted_channels = []
    for channel in channels:
        formatted_channels.append({
            "id": channel["id"],
            "name": channel["name"],
            "is_private": channel.get("is_private", False)
        })
    
    print(f"Found {len(formatted_channels)} channels in {course} workspace")
    return formatted_channels

@function_tool()
def read_slack_messages(channel_id: str, limit: int, course: str) -> List[Dict[str, Any]]:
    """
    Read messages from a Slack channel.
    
    Args:
        channel_id (str): The ID of the channel to read messages from
        limit (int): Maximum number of messages to retrieve
        course (str): Which course to use ("math" or "cse")
        
    Returns:
        List[Dict[str, Any]]: A list of message objects with text, user, timestamp, and attachments
    """
    # Handle default internally
    if not course or course.lower() not in ["math", "cse"]:
        course = "math"
    
    # Determine which token to use
    token = SLACK_TOKEN_MATH if course.lower() == "math" else SLACK_TOKEN_CSE
    
    # Create a Slack client
    client = WebClient(token=token)
    
    print(f"Reading messages from channel {channel_id} in {course} workspace")
    
    # Get the messages
    response = client.conversations_history(channel=channel_id, limit=limit)
    messages = response["messages"]
    
    # Format the messages
    formatted_messages = []
    for msg in messages:
        # Get user info
        user_id = msg.get("user", "UNKNOWN")
        try:
            user_info = client.users_info(user=user_id)
            username = user_info["user"]["name"]
        except:
            username = f"Unknown User ({user_id})"
        
        formatted_messages.append({
            "id": msg["ts"],
            "content": msg.get("text", ""),
            "author": username,
            "timestamp": msg["ts"],
            "attachments": [att.get("url", "") for att in msg.get("attachments", [])]
        })
    
    print(f"Found {len(formatted_messages)} messages in channel {channel_id}")
    return formatted_messages

@function_tool()
def send_slack_message(channel: str, text: str, course: str) -> Dict[str, Any]:
    """
    Send a message to a Slack channel.
    
    Args:
        channel (str): The channel to send the message to (e.g., "#general" or channel ID)
        text (str): The message text
        course (str): Which course to use ("math" or "cse")
        
    Returns:
        Dict[str, Any]: Information about the sent message, including channel and timestamp
    """
    # Handle default internally
    if not course or course.lower() not in ["math", "cse"]:
        course = "math"
    
    # Determine which token to use
    token = SLACK_TOKEN_MATH if course.lower() == "math" else SLACK_TOKEN_CSE
    
    # Create a Slack client
    client = WebClient(token=token)
    
    print(f"Sending message to {channel} in {course} workspace")
    
    # Send the message
    response = client.chat_postMessage(
        channel=channel,
        text=text
    )
    
    # Return the message information
    return {
        "id": response["ts"],
        "channel": channel,
        "timestamp": response["ts"]
    }

@function_tool()
def monitor_slack_channel(channel_id: str, duration: int, course: str) -> List[Dict[str, Any]]:
    """
    Monitor a Slack channel for new messages for a specified duration.
    
    Args:
        channel_id (str): The ID of the channel to monitor
        duration (int): How long to monitor the channel (in seconds)
        course (str): Which course to use ("math" or "cse")
        
    Returns:
        List[Dict[str, Any]]: A list of new messages that appeared during monitoring
    """
    # Handle defaults internally
    if not duration or duration <= 0:
        duration = 60
    
    if not course or course.lower() not in ["math", "cse"]:
        course = "math"
    
    # Create a Slack client
    client = WebClient(token=SLACK_TOKEN_MATH if course.lower() == "math" else SLACK_TOKEN_CSE)
    
    # Get the channel info to display the name
    channel_info = client.conversations_info(channel=channel_id)
    channel_name = channel_info["channel"]["name"]
    
    print(f"Monitoring channel: {channel_name} (ID: {channel_id}) for {duration} seconds")
    
    # Get initial messages to establish a baseline
    response = client.conversations_history(channel=channel_id, limit=1)
    latest_ts = response["messages"][0]["ts"] if response["messages"] else "0"
    
    # Store all new messages
    all_new_messages = []
    
    # Monitor for the specified duration
    end_time = time.time() + duration
    while time.time() < end_time:
        # Wait a bit before checking again
        time.sleep(5)
        
        # Get new messages
        response = client.conversations_history(channel=channel_id, oldest=latest_ts)
        messages = response["messages"]
        
        # Skip the first message if it's the same as our latest
        if messages and messages[0]["ts"] == latest_ts:
            messages = messages[1:]
        
        # Process new messages
        if messages:
            print(f"Found {len(messages)} new messages")
            
            # Update latest timestamp
            latest_ts = messages[0]["ts"]
            
            # Format and add the messages
            for msg in reversed(messages):
                # Get user info
                user_id = msg.get("user", "UNKNOWN")
                try:
                    user_info = client.users_info(user=user_id)
                    username = user_info["user"]["name"]
                except:
                    username = f"Unknown User ({user_id})"
                
                # Convert timestamp to readable format
                ts = float(msg["ts"])
                dt = datetime.fromtimestamp(ts)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                
                # Format the message
                formatted_msg = {
                    "text": msg.get("text", ""),
                    "user": username,
                    "timestamp": time_str,
                    "raw_timestamp": msg["ts"],
                    "attachments": [
                        {"title": att.get("title", "Untitled"), "url": att.get("url", "")} 
                        for att in msg.get("attachments", [])
                    ]
                }
                
                all_new_messages.append(formatted_msg)
                print(f"[{time_str}] {username}: {msg.get('text', '')}")
    
    print(f"Monitoring complete. Found {len(all_new_messages)} new messages.")
    return all_new_messages

# Create the function tools for the agent
'''
list_slack_channels = function_tool()(_list_slack_channels)
read_slack_messages = function_tool()(_read_slack_messages)
send_slack_message = function_tool()(_send_slack_message)
monitor_slack_channel = function_tool()(_monitor_slack_channel)
'''
def create_slack_agent():
    """Create a Slack agent with OpenAI."""
    return Agent(
        name="slack-agent",
        instructions=(
            "You are an assistant that helps users interact with Slack. "
            "You can list channels in a Slack workspace, read messages from channels, "
            "send messages to channels, and monitor channels for new messages."
        ),
        tools=[
            list_slack_channels,
            read_slack_messages,
            send_slack_message,
            monitor_slack_channel
        ],
        model="gpt-4o-mini",
    )
'''
# Create the Slack agent when the module is imported
slack_agent = create_slack_agent()

# Manual test function
def manual_test():
    """Run a manual test of the Slack functions."""
    print("=== Testing Slack Functions ===")
    
    # Test listing channels
    course_input = input("Enter course (math/cse) [default: math]: ")
    course = course_input if course_input else "math"
    
    try:
        # Use the undecorated functions for testing
        print("\nListing channels...")
        channels = _list_slack_channels(course)
        print(f"Found {len(channels)} channels:")
        for channel in channels:
            print(f"- {channel['name']} (ID: {channel['id']}, Private: {channel['is_private']})")
        
        # Test reading messages
        if channels:
            channel_id = input("\nEnter channel ID to read messages from: ")
            limit = input("Enter number of messages to retrieve [default: 10]: ")
            limit = int(limit) if limit.isdigit() else 10
            
            print(f"\nReading messages from channel {channel_id}...")
            messages = _read_slack_messages(channel_id, limit, course)
            print(f"Found {len(messages)} messages:")
            for msg in messages[:5]:  # Show first 5 for brevity
                print(f"- {msg['author']}: {msg['content']}")
    
        # Test sending a message
        send_msg = input("\nDo you want to send a test message? (y/n): ")
        if send_msg.lower() == 'y':
            channel = input("Enter channel name or ID: ")
            message = input("Enter message: ")
            
            print(f"\nSending message to {channel}...")
            result = _send_slack_message(channel, message, course)
            print(f"Message sent: {result['id']}")
        
        # Test running the agent
        run_agent = input("\nDo you want to test the agent? (y/n): ")
        if run_agent.lower() == 'y':
            from agents import Runner
            import asyncio
            
            async def test_agent():
                prompt = input("\nEnter a prompt for the Slack agent: ")
                result = await Runner.run(slack_agent, prompt)
                print(f"\nAgent response:\n{result.final_output}")
            
            asyncio.run(test_agent())
    
    except Exception as e:
        print(f"Error: {e}")
'''
def main():
    """Main function to create and run the Slack agent."""
    slack_agent = create_slack_agent()
    
    # Interactive loop
    user_input = None
    result = None
    
    print("=== Slack Agent ===")
    print("Type 'exit' or 'quit' to end the session")
    
    while True:
        user_input = input(" > ")
        
        if user_input.lower() in ["exit", "quit"]:
            break
        
        if result is not None:
            user_input = result.to_input_list() + [{"role": "user", "content": user_input}]
        
        result = Runner.run_sync(slack_agent, user_input)
        
        print("----\n" + f"{result.final_output}")

if __name__ == "__main__":
    # Run the manual test if the script is executed directly
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        manual_test()
    else:
        print("Slack Agent Module")
        print("-----------------")
        print("This module provides Slack functions for use with OpenAI agents.")
        print("To use the Slack agent in your code, import it like this:")
        print("  from slack_agent.slack_agent import slack_agent")
        print("\nRun with --test to test the Slack functions and agent:")
        print("  python slack_agent.py --test")
        main()