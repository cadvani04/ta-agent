import os
import discord
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from agents import function_tool

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is not set")

@function_tool()
def send_discord_message(channel_id: str, content: str, embed_title: Optional[str] = None, embed_description: Optional[str] = None) -> Dict[str, Any]:
    """
    Send a message to a Discord channel.
    
    Args:
        channel_id (str): The ID of the channel to send the message to
        content (str): The text content of the message
        embed_title (str, optional): Title for an embed, if desired
        embed_description (str, optional): Description for an embed, if desired
        
    Returns:
        Dict[str, Any]: Information about the sent message, including id, content, and timestamp
    """
    BASE_URL = "https://discord.com/api/v10"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (https://example.com, v1.0)"
    }
    
    print(f"Sending message to channel {channel_id}")
    
    # Prepare the message data
    message_data = {"content": content}
    
    # Add embed if title or description is provided
    if embed_title or embed_description:
        embed = {}
        if embed_title:
            embed["title"] = embed_title
        if embed_description:
            embed["description"] = embed_description
        message_data["embeds"] = [embed]
    
    # Send the message
    url = f"{BASE_URL}/channels/{channel_id}/messages"
    response = requests.post(url, json=message_data, headers=headers)
    
    if response.status_code not in [200, 201]:
        raise Exception(f"Error sending message: {response.status_code} - {response.text}")
    
    message = response.json()
    
    print(f"Message sent successfully with ID: {message['id']}")
    
    # Return a formatted response
    return {
        "id": message["id"],
        "content": message["content"],
        "channel_id": channel_id,
        "timestamp": message["timestamp"]
    }

@function_tool()
def edit_discord_message(channel_id: str, message_id: str, new_content: str) -> Dict[str, Any]:
    """
    Edit an existing Discord message.
    
    Args:
        channel_id (str): The ID of the channel containing the message
        message_id (str): The ID of the message to edit
        new_content (str): The new content for the message
        
    Returns:
        Dict[str, Any]: Information about the edited message
    """
    BASE_URL = "https://discord.com/api/v10"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (https://example.com, v1.0)"
    }
    
    print(f"Editing message {message_id} in channel {channel_id}")
    
    # Prepare the edit data
    edit_data = {"content": new_content}
    
    # Send the edit request
    url = f"{BASE_URL}/channels/{channel_id}/messages/{message_id}"
    response = requests.patch(url, json=edit_data, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error editing message: {response.status_code} - {response.text}")
    
    edited_message = response.json()
    
    print(f"Message edited successfully")
    
    # Return a formatted response
    return {
        "id": edited_message["id"],
        "content": edited_message["content"],
        "channel_id": channel_id,
        "edited_timestamp": edited_message.get("edited_timestamp")
    }

@function_tool()
def delete_discord_message(channel_id: str, message_id: str) -> Dict[str, bool]:
    """
    Delete a Discord message.
    
    Args:
        channel_id (str): The ID of the channel containing the message
        message_id (str): The ID of the message to delete
        
    Returns:
        Dict[str, bool]: Status of the deletion operation
    """
    BASE_URL = "https://discord.com/api/v10"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (https://example.com, v1.0)"
    }
    
    print(f"Deleting message {message_id} from channel {channel_id}")
    
    # Send the delete request
    url = f"{BASE_URL}/channels/{channel_id}/messages/{message_id}"
    response = requests.delete(url, headers=headers)
    
    # Check if deletion was successful (Discord returns 204 No Content on success)
    if response.status_code != 204:
        raise Exception(f"Error deleting message: {response.status_code} - {response.text}")
    
    print(f"Message deleted successfully")
    
    # Return success status
    return {
        "success": True,
        "channel_id": channel_id,
        "message_id": message_id
    }

# For testing purposes
def manual_test():
    """Test the Discord message functions manually."""
    print("=== Testing Discord Write Functions ===")
    
    #channel_id = input("Enter Discord channel ID: ")
    channel_id = "1365757421938544721"
    
    # Test sending a message
    print("\nTesting send_discord_message:")
    message_content = input("Enter message content: ")
    
    try:
        sent_message = send_discord_message(channel_id, message_content)
        print(f"Message sent successfully with ID: {sent_message['id']}")
        message_id = sent_message['id']
        
        # Test editing the message
        edit_option = input("\nDo you want to edit this message? (y/n): ")
        if edit_option.lower() == 'y':
            new_content = input("Enter new message content: ")
            edited_message = edit_discord_message(channel_id, message_id, new_content)
            print(f"Message edited successfully at: {edited_message.get('edited_timestamp')}")
        
        # Test deleting the message
        delete_option = input("\nDo you want to delete this message? (y/n): ")
        if delete_option.lower() == 'y':
            delete_result = delete_discord_message(channel_id, message_id)
            if delete_result['success']:
                print("Message deleted successfully")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    manual_test()
