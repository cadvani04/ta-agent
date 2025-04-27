"""
Canvas Groups API

This module provides functions to interact with the Canvas Groups API.
https://canvas.instructure.com/doc/api/groups.html

It includes functionality to:
- List groups in a context (course/account)
- Get a single group
- Create a group
- List group users
- Manage group memberships
"""

import os
import requests
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from canvasapi import Canvas
from agents import function_tool

# Load environment variables
load_dotenv()
CANVAS_API_URL = os.getenv('CANVAS_API_URL', 'https://canvas.instructure.com/api/v1')
CANVAS_API_TOKEN = os.getenv('canvas_token')

def get_canvas():
    """Get a Canvas API client instance."""
    if not CANVAS_API_TOKEN:
        raise ValueError("Canvas API token not found in environment variables")
    return Canvas(CANVAS_API_URL, CANVAS_API_TOKEN)

class GroupUser(BaseModel):
    """Model for a user in a group."""
    id: int
    name: str
    sortable_name: Optional[str] = None
    short_name: Optional[str] = None
    login_id: Optional[str] = None

class Group(BaseModel):
    """Model for a Canvas group."""
    id: int
    name: str
    description: Optional[str] = None
    is_public: Optional[bool] = None
    followed_by_user: Optional[bool] = None
    join_level: Optional[str] = None
    members_count: Optional[int] = None
    avatar_url: Optional[str] = None
    context_type: Optional[str] = None
    course_id: Optional[int] = None
    account_id: Optional[int] = None
    role: Optional[str] = None

#@function_tool()
def list_groups_in_context(context_type: str, context_id: int) -> List[Dict[str, Any]]:
    print(f"Listing groups in {context_type} {context_id}")
    """
    List the groups available in a specific context (course or account).
    
    Args:
        context_type (str): The context type, either 'course' or 'account'
        context_id (int): The Canvas course ID or account ID
        
    Returns:
        List[Dict[str, Any]]: A list of groups in the specified context
    """
    canvas = get_canvas()
    
    if context_type not in ['course', 'account']:
        raise ValueError("context_type must be either 'course' or 'account'")
    
    url = f"{CANVAS_API_URL}/{context_type}s/{context_id}/groups"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching groups: {response.status_code} - {response.text}")
    
    groups = response.json()
    print(f"Found {len(groups)} groups in {context_type} {context_id}")
    
    return groups

#@function_tool()
def get_group(group_id: int) -> Dict[str, Any]:
    """
    Get information about a specific group.
    
    Args:
        group_id (int): The Canvas group ID
        
    Returns:
        Dict[str, Any]: Information about the group
    """
    canvas = get_canvas()
    
    url = f"{CANVAS_API_URL}/groups/{group_id}"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching group: {response.status_code} - {response.text}")
    
    group = response.json()
    print(f"Retrieved group: {group.get('name', 'Unknown')}")
    
    return group

#@function_tool()
def create_group(name: str, description: Optional[str] = None, join_level: Optional[str] = None, is_public: Optional[bool] = None, context_type: Optional[str] = None, context_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Create a new group.
    
    Args:
        name (str): The name of the group
        description (str, optional): A description of the group
        join_level (str, optional): 'parent_context_auto_join', 'parent_context_request', or 'invitation_only'
        is_public (bool, optional): Whether the group is public (true) or private (false)
        context_type (str, optional): The context type, either 'course' or 'account'
        context_id (int, optional): The Canvas course ID or account ID
        
    Returns:
        Dict[str, Any]: Information about the created group
    """
    print(f"Creating group with name: {name}")
    canvas = get_canvas()
    
    # Determine the endpoint based on whether we're creating in a context
    if context_type and context_id:
        if context_type not in ['course', 'account']:
            raise ValueError("context_type must be either 'course' or 'account'")
        url = f"{CANVAS_API_URL}/{context_type}s/{context_id}/groups"
    else:
        url = f"{CANVAS_API_URL}/groups"
    
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    
    data = {"name": name}
    if description:
        data["description"] = description
    if join_level:
        data["join_level"] = join_level
    if is_public is not None:
        data["is_public"] = is_public
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code not in [200, 201]:
        raise Exception(f"Error creating group: {response.status_code} - {response.text}")
    
    group = response.json()
    print(f"Created group: {group.get('name', 'Unknown')}")
    
    return group

#@function_tool()
def list_group_users(group_id: int) -> List[Dict[str, Any]]:
    """
    List the users in a specific group.
    
    Args:
        group_id (int): The Canvas group ID
        
    Returns:
        List[Dict[str, Any]]: A list of users in the group
    """
    canvas = get_canvas()
    
    url = f"{CANVAS_API_URL}/groups/{group_id}/users"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching group users: {response.status_code} - {response.text}")
    
    users = response.json()
    print(f"Found {len(users)} users in group {group_id}")
    
    return users

#@function_tool()
def add_user_to_group(group_id: int, user_id: int) -> Dict[str, Any]:
    """
    Add a user to a group.
    
    Args:
        group_id (int): The Canvas group ID
        user_id (int): The Canvas user ID
        
    Returns:
        Dict[str, Any]: Information about the created membership
    """
    canvas = get_canvas()
    
    url = f"{CANVAS_API_URL}/groups/{group_id}/memberships"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    
    data = {"user_id": user_id}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code not in [200, 201]:
        raise Exception(f"Error adding user to group: {response.status_code} - {response.text}")
    
    membership = response.json()
    print(f"Added user {user_id} to group {group_id}")
    
    return membership

#@function_tool()
def remove_user_from_group(group_id: int, user_id: int) -> Dict[str, Any]:
    """
    Remove a user from a group.
    
    Args:
        group_id (int): The Canvas group ID
        user_id (int): The Canvas user ID
        
    Returns:
        Dict[str, Any]: Information about the deleted membership
    """
    canvas = get_canvas()
    
    url = f"{CANVAS_API_URL}/groups/{group_id}/users/{user_id}"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error removing user from group: {response.status_code} - {response.text}")
    
    result = response.json()
    print(f"Removed user {user_id} from group {group_id}")
    
    return result

@function_tool()
def get_group_activity_stream(group_id: int) -> List[Dict[str, Any]]:
    """
    Get the activity stream for a group.
    
    Args:
        group_id (int): The Canvas group ID
        
    Returns:
        List[Dict[str, Any]]: A list of activity stream items
    """
    canvas = get_canvas()
    
    url = f"{CANVAS_API_URL}/groups/{group_id}/activity_stream"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching group activity stream: {response.status_code} - {response.text}")
    
    activities = response.json()
    print(f"Found {len(activities)} activity items for group {group_id}")
    
    return activities

# Example usage
if __name__ == "__main__":
    # Replace with actual IDs for testing
    test_course_id = 11883051
    
    try:
        print("Listing groups in course...")
        groups = list_groups_in_context('course', test_course_id)
        
        if groups:
            # Get the first group for further testing
            test_group_id = groups[0]['id']
            
            print("\nGetting group details...")
            group = get_group(test_group_id)
            
            print("\nListing group users...")
            users = list_group_users(test_group_id)
            
            print("\nGetting group activity stream...")
            activities = get_group_activity_stream(test_group_id)
        else:
            print("\nCreating a test group...")
            new_group = create_group(
                name="Test Group",
                description="A test group created via API",
                join_level="invitation_only",
                is_public=False,
                context_type="course",
                context_id=test_course_id
            )
            
    except Exception as e:
        print(f"Error: {e}")
