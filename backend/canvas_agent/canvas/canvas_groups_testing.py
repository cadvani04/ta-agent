import os
import sys
import time
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from agents import Agent, Runner, function_tool

# Import the groups functions
from canvas_groups import (
    list_groups_in_context,
    get_group,
    create_group,
    list_group_users,
    add_user_to_group,
    get_group_activity_stream
)
print("Canvas groups functions imported")

# Load environment variables
load_dotenv()
CANVAS_API_TOKEN = os.getenv('canvas_token')
CANVAS_API_URL = os.getenv('CANVAS_API_URL', 'https://canvas.instructure.com')

# Default course ID for testing
DEFAULT_COURSE_ID = 11883051  # Replace with your actual course ID

def test_list_groups():
    print("\n=== Testing List Groups in Context ===")
    course_id = DEFAULT_COURSE_ID
    print(f"Using course ID: {course_id}")
    
    try:
        groups = list_groups_in_context('course', course_id)
        
        print(f"Found {len(groups)} groups")
        if groups:
            print("\nSample groups:")
            for group in groups[:3]:  # Show first 3 for brevity
                print(f"Group: {group.get('name', 'N/A')} (ID: {group.get('id', 'N/A')})")
                print(f"Members: {group.get('members_count', 'N/A')}")
                print("---")
            
            # Return the first group ID for further tests
            return groups[0]['id']
        else:
            print("No groups found. Will create a test group.")
            return None
    except Exception as e:
        print(f"Error listing groups: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_create_group():
    print("\n=== Testing Create Group ===")
    course_id = DEFAULT_COURSE_ID
    print(f"Using course ID: {course_id}")
    
    try:
        group_name = f"Test Group {int(time.time())}"
        print(f"Creating group with name: {group_name}")
        
        # Create a simple group with minimal parameters
        group = create_group(
            name=group_name,
            context_type="course",
            context_id=course_id
        )
        
        print(f"Created group: {group.get('name', 'N/A')} (ID: {group.get('id', 'N/A')})")
        return group.get('id')
    except Exception as e:
        print(f"Error creating group: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_get_group(group_id):
    if not group_id:
        print("No group ID available. Skipping get group test.")
        return
    
    print(f"\n=== Testing Get Group {group_id} ===")
    
    try:
        group = get_group(group_id)
        
        print(f"Group: {group.get('name', 'N/A')}")
        print(f"Description: {group.get('description', 'N/A')}")
        print(f"Join Level: {group.get('join_level', 'N/A')}")
        print(f"Members Count: {group.get('members_count', 'N/A')}")
    except Exception as e:
        print(f"Error getting group: {e}")

def test_list_group_users(group_id):
    if not group_id:
        print("No group ID available. Skipping list group users test.")
        return
    
    print(f"\n=== Testing List Group Users for Group {group_id} ===")
    
    try:
        users = list_group_users(group_id)
        
        print(f"Found {len(users)} users in group")
        if users:
            print("\nGroup users:")
            for user in users[:5]:  # Show first 5 for brevity
                print(f"User: {user.get('name', 'N/A')} (ID: {user.get('id', 'N/A')})")
            
            # Return the first user ID for further tests
            return users[0]['id'] if users else None
        else:
            print("No users found in this group")
            return None
    except Exception as e:
        print(f"Error listing group users: {e}")
        return None

def test_group_activity_stream(group_id):
    if not group_id:
        print("No group ID available. Skipping group activity stream test.")
        return
    
    print(f"\n=== Testing Group Activity Stream for Group {group_id} ===")
    
    try:
        activities = get_group_activity_stream(group_id)
        
        print(f"Found {len(activities)} activity items")
        if activities:
            print("\nRecent activities:")
            for activity in activities[:3]:  # Show first 3 for brevity
                print(f"Type: {activity.get('type', 'N/A')}")
                print(f"Title: {activity.get('title', 'N/A')}")
                print(f"Created at: {activity.get('created_at', 'N/A')}")
                print("---")
        else:
            print("No activity items found for this group")
    except Exception as e:
        print(f"Error getting group activity stream: {e}")

def interactive_session():
    print("\n=== Interactive Canvas Groups Session ===")
    print("Type 'exit' or 'quit' to end the session")
    print("Available commands:")
    print("  list <course_id> - List groups in a course")
    print("  create <course_id> <name> - Create a new group in a course")
    print("  get <group_id> - Get details of a group")
    print("  users <group_id> - List users in a group")
    print("  activity <group_id> - Get activity stream for a group")
    
    while True:
        user_input = input(" > ")

        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            parts = user_input.split()
            command = parts[0].lower()
            
            if command == "list" and len(parts) >= 2:
                course_id = int(parts[1])
                groups = list_groups_in_context('course', course_id)
                print(f"Found {len(groups)} groups:")
                for group in groups[:5]:  # Show first 5 for brevity
                    print(f"- {group.get('name', 'N/A')} (ID: {group.get('id', 'N/A')})")
                    
            elif command == "create" and len(parts) >= 3:
                course_id = int(parts[1])
                name = " ".join(parts[2:])
                group = create_group(name=name, context_type="course", context_id=course_id)
                print(f"Created group: {group.get('name', 'N/A')} (ID: {group.get('id', 'N/A')})")
                
            elif command == "get" and len(parts) >= 2:
                group_id = int(parts[1])
                group = get_group(group_id)
                print(f"Group: {group.get('name', 'N/A')}")
                print(f"Description: {group.get('description', 'N/A')}")
                print(f"Members Count: {group.get('members_count', 'N/A')}")
                
            elif command == "users" and len(parts) >= 2:
                group_id = int(parts[1])
                users = list_group_users(group_id)
                print(f"Found {len(users)} users:")
                for user in users[:5]:  # Show first 5 for brevity
                    print(f"- {user.get('name', 'N/A')} (ID: {user.get('id', 'N/A')})")
                    
            elif command == "activity" and len(parts) >= 2:
                group_id = int(parts[1])
                activities = get_group_activity_stream(group_id)
                print(f"Found {len(activities)} activity items")
                for activity in activities[:3]:  # Show first 3 for brevity
                    print(f"- Type: {activity.get('type', 'N/A')}")
                    print(f"  Title: {activity.get('title', 'N/A')}")
                    
            else:
                print("Unknown command or invalid arguments")
                
        except Exception as e:
            print(f"Error: {e}")

def main():
    # Check if Canvas token is set
    if not CANVAS_API_TOKEN:
        print("Error: canvas_token must be set in .env file")
        sys.exit(1)
    print("Canvas token is set")

    print(f"Using Canvas API URL: {CANVAS_API_URL}")
    print(f"Using Canvas token: {CANVAS_API_TOKEN[:10]}...")

    # Run simplified tests
    print("\n--- Running Simplified Tests ---")
    
    # First try to list existing groups
    group_id = test_list_groups()
    
    # If no groups found, create one
    if not group_id:
        group_id = test_create_group()
    
    # Test getting group details
    test_get_group(group_id)
    
    # Test listing group users
    test_list_group_users(group_id)
    
    # Test group activity stream
    test_group_activity_stream(group_id)
    
    # Run interactive session
    interactive_session()

def test_with_agent():
    """
    Test the Canvas Groups functions using the Agent framework.
    This function creates an AI agent that can use the Canvas Groups functions
    to respond to natural language queries about Canvas groups.
    """
    print("\n=== Testing Canvas Groups with Agent ===")
    
    # Create the agent with the Canvas Groups functions as tools
    agent = Agent(
        name="canvas-groups-agent",
        instructions=(
            "You are an assistant designed to help the user manage Canvas groups. "
            "You can list groups in a course, get group details, create groups, "
            "list group users, add users to groups, and get group activity streams. "
            f"The default course ID for testing is {DEFAULT_COURSE_ID}."
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
    
    # Example queries to test
    test_queries = [
        f"List all groups in course {DEFAULT_COURSE_ID}",
        f"Create a new group called 'Test Agent Group' in course {DEFAULT_COURSE_ID}",
        "Tell me about the groups you just found or created"
    ]
    
    # Run each test query
    result = None
    for i, query in enumerate(test_queries):
        print(f"\nTest Query {i+1}: {query}")
        
        # For the first query, just use the query text
        # For subsequent queries, include the conversation history
        if result is None:
            input_data = query
        else:
            input_data = result.to_input_list() + [{"role": "user", "content": query}]
        
        # Run the agent
        result = Runner.run_sync(agent, input_data)
        
        # Print the result
        print(f"Agent Response: {result.final_output}")
    
    # Interactive session with the agent
    print("\n=== Interactive Agent Session ===")
    print("Type 'exit' or 'quit' to end the session")
    
    user_input = None
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
        result = Runner.run_sync(agent, input_data)
        
        # Print the result
        print(f"Agent: {result.final_output}")

if __name__ == "__main__":
    # Uncomment the function you want to run
    main()
    # test_with_agent() 