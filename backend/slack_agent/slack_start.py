import os
import sys
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from datetime import datetime
import time

# Load environment variables
load_dotenv()

def send_message(channel, text, token_env_var="SLACK_BOT_MATH"):
    """
    Send a message to a Slack channel.
    
    Args:
        channel (str): The channel to send the message to (e.g., "#general")
        text (str): The message text
        token_env_var (str): The name of the environment variable containing the token
        
    Returns:
        dict: The response from the Slack API
    """
    # Get the token from environment variables
    token = os.environ.get(token_env_var)
    
    if not token:
        print(f"Error: {token_env_var} environment variable not found")
        return None
    
    print(f"Using token from {token_env_var}: {token[:10]}...")
    
    # Create a Slack client
    client = WebClient(token=token)
    
    try:
        # Send the message
        response = client.chat_postMessage(
            channel=channel,
            text=text
        )
        print(f"Message sent to {channel}, timestamp: {response['ts']}")
        return response
    except SlackApiError as e:
        error = e.response["error"]
        print(f"Error posting message: {error}")
        
        # Provide more helpful error messages based on the error type
        if error == "missing_scope":
            print("\nPermission Error: Your bot token doesn't have the required permissions.")
            print("Please add the following scopes to your Slack app:")
            print("- chat:write (to send messages)")
            print("- channels:read (to view public channels)")
            print("- groups:read (to view private channels)")
            print("- im:read (to view direct messages)")
        elif error == "channel_not_found":
            print(f"\nChannel Error: The channel '{channel}' was not found or your bot doesn't have access to it.")
            print("Make sure the channel exists and your bot has been invited to it.")
        elif error == "not_in_channel":
            print(f"\nAccess Error: Your bot is not a member of the channel '{channel}'.")
            print(f"Please invite your bot to the channel by typing '/invite @YourBotName' in {channel}.")
        elif error == "invalid_auth":
            print("\nAuthentication Error: The token is invalid or expired.")
            print("Please check your token and make sure it's correct.")
        
        return None

def list_channels(token_env_var="SLACK_BOT_MATH"):
    """
    List all channels the bot has access to.
    
    Args:
        token_env_var (str): The name of the environment variable containing the token
        
    Returns:
        list: A list of channel objects
    """
    # Get the token from environment variables
    token = os.environ.get(token_env_var)
    
    if not token:
        print(f"Error: {token_env_var} environment variable not found")
        return None
    
    # Create a Slack client
    client = WebClient(token=token)
    
    try:
        # Get the list of channels
        response = client.conversations_list(types="public_channel,private_channel")
        channels = response["channels"]
        
        print(f"Found {len(channels)} channels:")
        for channel in channels:
            print(f"- {channel['name']} (ID: {channel['id']}, Private: {channel.get('is_private', False)})")
        
        return channels
    except SlackApiError as e:
        error = e.response["error"]
        print(f"Error listing channels: {error}")
        
        # Provide more helpful error messages based on the error type
        if error == "missing_scope":
            print("\nPermission Error: Your bot token doesn't have the required permissions.")
            print("Please add the following scopes to your Slack app:")
            print("- channels:read (to view public channels)")
            print("- groups:read (to view private channels)")
        
        return None


def read_messages(channel_id, limit=10, token_env_var="SLACK_BOT_MATH"):
    """
    Read messages from a Slack channel.
    
    Args:
        channel_id (str): The ID of the channel to read messages from
        limit (int): Maximum number of messages to retrieve
        token_env_var (str): The name of the environment variable containing the token
        
    Returns:
        list: A list of message objects
    """
    # Get the token from environment variables
    token = os.environ.get(token_env_var)
    
    if not token:
        print(f"Error: {token_env_var} environment variable not found")
        return None
    
    # Create a Slack client
    client = WebClient(token=token)
    
    try:
        # Get the channel info to display the name
        channel_info = client.conversations_info(channel=channel_id)
        channel_name = channel_info["channel"]["name"]
        
        print(f"Reading messages from channel: {channel_name} (ID: {channel_id})")
        
        # Get the messages
        response = client.conversations_history(channel=channel_id, limit=limit)
        messages = response["messages"]
        
        print(f"Found {len(messages)} messages:")
        
        # Format and display the messages
        formatted_messages = []
        for msg in messages:
            # Convert timestamp to readable format
            ts = float(msg["ts"])
            dt = datetime.fromtimestamp(ts)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            
            # Get user info
            user_id = msg.get("user", "UNKNOWN")
            try:
                user_info = client.users_info(user=user_id)
                username = user_info["user"]["name"]
            except:
                username = f"Unknown User ({user_id})"
            
            # Format the message
            formatted_msg = {
                "text": msg.get("text", ""),
                "user": username,
                "time": time_str,
                "reactions": msg.get("reactions", []),
                "attachments": msg.get("attachments", []),
                "thread_ts": msg.get("thread_ts")
            }
            
            formatted_messages.append(formatted_msg)
            
            # Print the message
            print(f"[{time_str}] {username}: {msg.get('text', '')}")
            
            # Print attachments if any
            if "attachments" in msg and msg["attachments"]:
                print(f"  Attachments: {len(msg['attachments'])}")
                for att in msg["attachments"]:
                    if "title" in att:
                        print(f"  - {att['title']}")
            
            # Print reactions if any
            if "reactions" in msg and msg["reactions"]:
                reactions_str = ", ".join([f"{r['name']} ({r['count']})" for r in msg["reactions"]])
                print(f"  Reactions: {reactions_str}")
            
            print("---")
        
        return formatted_messages
    
    except SlackApiError as e:
        error = e.response["error"]
        print(f"Error reading messages: {error}")
        
        # Provide more helpful error messages based on the error type
        if error == "missing_scope":
            print("\nPermission Error: Your bot token doesn't have the required permissions.")
            print("Please add the following scopes to your Slack app:")
            print("- channels:history (to read channel messages)")
            print("- users:read (to get user information)")
        elif error == "channel_not_found":
            print(f"\nChannel Error: The channel with ID '{channel_id}' was not found or your bot doesn't have access to it.")
        
        return None


def monitor_channel(channel_id, interval=5, token_env_var="SLACK_BOT_MATH"):
    """
    Monitor a Slack channel for new messages.
    
    Args:
        channel_id (str): The ID of the channel to monitor
        interval (int): How often to check for new messages (in seconds)
        token_env_var (str): The name of the environment variable containing the token
    """
    # Get the token from environment variables
    token = os.environ.get(token_env_var)
    
    if not token:
        print(f"Error: {token_env_var} environment variable not found")
        return
    
    # Create a Slack client
    client = WebClient(token=token)
    
    try:
        # Get the channel info to display the name
        channel_info = client.conversations_info(channel=channel_id)
        channel_name = channel_info["channel"]["name"]
        
        print(f"Monitoring channel: {channel_name} (ID: {channel_id})")
        print(f"Press Ctrl+C to stop monitoring")
        
        # Get initial messages to establish a baseline
        response = client.conversations_history(channel=channel_id, limit=1)
        latest_ts = response["messages"][0]["ts"] if response["messages"] else "0"
        
        while True:
            # Wait for the specified interval
            time.sleep(interval)
            
            # Get new messages
            response = client.conversations_history(channel=channel_id, oldest=latest_ts)
            messages = response["messages"]
            
            # Skip the first message if it's the same as our latest
            if messages and messages[0]["ts"] == latest_ts:
                messages = messages[1:]
            
            # Process new messages
            if messages:
                print(f"\nFound {len(messages)} new messages:")
                
                # Update latest timestamp
                latest_ts = messages[0]["ts"]
                
                # Display the messages in reverse order (oldest first)
                for msg in reversed(messages):
                    # Convert timestamp to readable format
                    ts = float(msg["ts"])
                    dt = datetime.fromtimestamp(ts)
                    time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Get user info
                    user_id = msg.get("user", "UNKNOWN")
                    try:
                        user_info = client.users_info(user=user_id)
                        username = user_info["user"]["name"]
                    except:
                        username = f"Unknown User ({user_id})"
                    
                    # Print the message
                    print(f"[{time_str}] {username}: {msg.get('text', '')}")
                    
                    # Print attachments if any
                    if "attachments" in msg and msg["attachments"]:
                        print(f"  Attachments: {len(msg['attachments'])}")
                        for att in msg["attachments"]:
                            if "title" in att:
                                print(f"  - {att['title']}")
                    
                    print("---")
    
    except KeyboardInterrupt:
        print("\nStopped monitoring channel")
    
    except SlackApiError as e:
        error = e.response["error"]
        print(f"Error monitoring channel: {error}")
        
        # Provide more helpful error messages based on the error type
        if error == "missing_scope":
            print("\nPermission Error: Your bot token doesn't have the required permissions.")
            print("Please add the following scopes to your Slack app:")
            print("- channels:history (to read channel messages)")
            print("- users:read (to get user information)")
        elif error == "channel_not_found":
            print(f"\nChannel Error: The channel with ID '{channel_id}' was not found or your bot doesn't have access to it.")

def main():
    """Run a simple test of the Slack bot."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Test the Slack bot')
    parser.add_argument('--course', choices=['math', 'cse'], default='math',
                      help='Which course to use (math or cse)')
    parser.add_argument('--action', choices=['send', 'list', 'read', 'monitor'], default='read',
                      help='Action to perform (send message, list channels, read messages, or monitor channel)')
    args = parser.parse_args()
    
    # Determine which token to use
    token_env_var = "SLACK_BOT_MATH" if args.course == 'math' else "SLACK_BOT_CSE"
    
    # Perform the requested action
    if args.action == 'send':
        channel = input("Enter channel name (e.g., #general): ")
        message = input("Enter message: ")
        send_message(channel, message, token_env_var)
    
    elif args.action == 'list':
        list_channels(token_env_var)
    
    elif args.action == 'read':
        # First list channels so the user can choose one
        channels = list_channels(token_env_var)
        if not channels:
            return
        
        # Ask the user which channel to read
        channel_id = input("\nEnter channel ID to read messages from: ")
        limit = input("Enter number of messages to retrieve (default: 10): ")
        limit = int(limit) if limit.isdigit() else 10
        
        read_messages(channel_id, limit, token_env_var)
    
    elif args.action == 'monitor':
        # First list channels so the user can choose one
        channels = list_channels(token_env_var)
        if not channels:
            return
        
        # Ask the user which channel to monitor
        channel_id = input("\nEnter channel ID to monitor: ")
        interval = input("Enter check interval in seconds (default: 5): ")
        interval = int(interval) if interval.isdigit() else 5
        
        monitor_channel(channel_id, interval, token_env_var)

if __name__ == "__main__":
    main()
