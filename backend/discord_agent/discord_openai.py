import os
import discord
import requests
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from agents import function_tool

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if not DISCORD_TOKEN:
    raise ValueError("discord_token environment variable is not set")

# Discord API functions
@function_tool()
def list_discord_channels(guild_id: str) -> List[Dict[str, Any]]:
    """
    List all channels in a Discord server.
    
    Args:
        guild_id (str): The ID of the Discord server (guild)
        
    Returns:
        List[Dict[str, Any]]: A list of channel objects with id, name, and type
    """
    BASE_URL = "https://discord.com/api/v10"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (https://example.com, v1.0)"
    }
    
    print(f"Listing channels in guild {guild_id}")
    
    url = f"{BASE_URL}/guilds/{guild_id}/channels"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching channels: {response.status_code} - {response.text}")
    
    channels = response.json()
    
    # Filter and format the channels
    formatted_channels = []
    for channel in channels:
        # Only include text channels (type 0) and categories (type 4)
        if channel["type"] in [0, 4]:
            formatted_channels.append({
                "id": channel["id"],
                "name": channel["name"],
                "type": channel["type"]
            })
    
    print(f"Found {len(formatted_channels)} channels in guild {guild_id}")
    return formatted_channels

@function_tool()
def read_discord_messages(guild_id: str, channel_id: str, limit: int, before: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Read messages from a Discord channel.
    
    Args:
        guild_id (str): The ID of the Discord server (guild)
        channel_id (str): The ID of the channel to read messages from
        limit (int): Maximum number of messages to retrieve.
        before (str, optional): Message ID to fetch messages before. Defaults to None.
        
    Returns:
        List[Dict[str, Any]]: A list of message objects with id, content, author, timestamp, and attachments
    """
    BASE_URL = "https://discord.com/api/v10"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (https://example.com, v1.0)"
    }
    
    print(f"Reading messages from guild {guild_id}, channel {channel_id}")
    
    # Build query parameters
    params = {"limit": limit}
    if before:
        params["before"] = before
    
    url = f"{BASE_URL}/channels/{channel_id}/messages"
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching messages: {response.status_code} - {response.text}")
    
    messages = response.json()
    
    # Format the messages
    formatted_messages = []
    for message in messages:
        formatted_messages.append({
            "id": message["id"],
            "content": message["content"],
            "author": message["author"]["username"],
            "timestamp": message["timestamp"],
            "attachments": [att["url"] for att in message["attachments"]]
        })
    
    print(f"Found {len(formatted_messages)} messages in channel {channel_id}")
    return formatted_messages

@function_tool()
def create_discord_server(name: str) -> Dict[str, Any]:
    """
    Create a new Discord server.
    
    Args:
        name (str): The name of the Discord server to create
        
    Returns:
        Dict[str, Any]: Information about the created server, including id, name, and invite link
    """
    BASE_URL = "https://discord.com/api/v10"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (https://example.com, v1.0)"
    }
    
    print(f"Creating Discord server: {name}")
    
    # Create guild
    guild_url = f"{BASE_URL}/guilds"
    guild_data = {"name": name}
    guild_response = requests.post(guild_url, json=guild_data, headers=headers)
    
    if guild_response.status_code != 201:
        raise Exception(f"Error creating server: {guild_response.status_code} - {guild_response.text}")
    
    guild = guild_response.json()
    guild_id = guild['id']
    print(f"Created server with ID: {guild_id}")
    
    # Create a general channel
    channel_url = f"{BASE_URL}/guilds/{guild_id}/channels"
    channel_data = {"name": "general", "type": 0}  # 0 = text channel
    channel_response = requests.post(channel_url, json=channel_data, headers=headers)
    
    if channel_response.status_code != 201:
        raise Exception(f"Error creating channel: {channel_response.status_code} - {channel_response.text}")
    
    channel = channel_response.json()
    channel_id = channel['id']
    print(f"Created channel with ID: {channel_id}")
    
    # Create an invite for the channel
    invite_url = f"{BASE_URL}/channels/{channel_id}/invites"
    invite_data = {
        "max_age": 0,  # Never expire
        "max_uses": 0,  # Unlimited uses
        "temporary": False
    }
    invite_response = requests.post(invite_url, json=invite_data, headers=headers)
    
    if invite_response.status_code != 200:
        raise Exception(f"Error creating invite: {invite_response.status_code} - {invite_response.text}")
    
    invite = invite_response.json()
    invite_code = invite['code']
    invite_link = f"https://discord.gg/{invite_code}"
    print(f"Created invite link: {invite_link}")
    
    # Return the guild information with the invite link
    return {
        "id": guild_id,
        "name": name,
        "invite_link": invite_link
    }

# Create a Discord client for real-time interaction
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def create_discord_agent():
    """Create a Discord agent with OpenAI."""
    from agents import Agent
    
    return Agent(
        name="discord-agent",
        instructions=(
            "You are an assistant that helps users interact with Discord. "
            "You can read messages from Discord channels, list channels in a Discord server, "
            "and create new Discord servers."
        ),
        tools=[
            list_discord_channels,
            read_discord_messages,
            create_discord_server
        ],
        model="gpt-4o-mini",
    )

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print("Discord agent initialized")

@client.event
async def on_message(message):
    # Don't respond to our own messages
    if message.author == client.user:
        return
    
    # Check if the message mentions the bot or is a DM
    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = client.user in message.mentions
    
    if is_dm or is_mentioned:
        # Remove the mention from the message content if present
        content = message.content
        if is_mentioned:
            content = content.replace(f'<@{client.user.id}>', '').strip()
        
        # Send a typing indicator to show the bot is processing
        async with message.channel.typing():
            try:
                # Run the agent with the message content
                from agents import Runner
                discord_agent = create_discord_agent()
                result = await Runner.run(discord_agent, content)
                
                # Send the response
                response = result.final_output
                
                # Split long messages if needed (Discord has a 2000 character limit)
                if len(response) > 1900:
                    chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                    for chunk in chunks:
                        await message.channel.send(chunk)
                else:
                    await message.channel.send(response)
            except Exception as e:
                await message.channel.send(f"Sorry, I encountered an error: {str(e)}")

# Manual test function
def manual_test():
    """Run a manual test of the Discord functions."""
    print("=== Testing Discord Functions ===")
    
    # Test listing channels
    guild_id = input("Enter Discord server ID: ")
    try:
        print("\nListing channels...")
        channels = list_discord_channels(guild_id)
        print(f"Found {len(channels)} channels:")
        for channel in channels:
            print(f"- {channel['name']} (ID: {channel['id']}, Type: {channel['type']})")
        
        # Test reading messages
        if channels:
            text_channels = [c for c in channels if c['type'] == 0]
            if text_channels:
                channel_id = text_channels[0]['id']
                print(f"\nReading messages from channel {text_channels[0]['name']}...")
                messages = read_discord_messages(guild_id, channel_id, limit=10)
                print(f"Found {len(messages)} messages:")
                for msg in messages[:5]:  # Show first 5 for brevity
                    print(f"- {msg['author']}: {msg['content']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test creating a server (optional)
    create_server = input("\nDo you want to test creating a server? (y/n): ")
    if create_server.lower() == 'y':
        server_name = input("Enter server name: ")
        try:
            print(f"\nCreating server '{server_name}'...")
            server = create_discord_server(server_name)
            print(f"Created server: {server['name']} (ID: {server['id']})")
            print(f"Invite link: {server['invite_link']}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Run the manual test or Discord client
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        manual_test()
    else:
        print("Starting Discord client...")
        client.run(DISCORD_TOKEN) 