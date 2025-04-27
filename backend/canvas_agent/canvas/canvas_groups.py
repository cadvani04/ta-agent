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
import requests
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from canvasapi import Canvas
from agents import function_tool

# Load environment variables
load_dotenv()
CANVAS_API_URL = os.getenv(
    'CANVAS_API_URL''https://canvas.instructure.com/api/v1')
CANVAS_API_TOKEN = os.getenv('canvas_token')


def get_canvas():
    """Get a Canvas API client instance."""
    if not CANVAS_API_TOKEN:
        raise ValueError("Canvas API token not found in environment variables")
    return Canvas(CANVAS_API_URL, CANVAS_API_TOKEN)
