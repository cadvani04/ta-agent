from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
from agents import Agent, RunContextWrapper, function_tool
from canvasapi import Canvas

# —————————————————————————————
# Pydantic models
# —————————————————————————————


from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

from pydantic import BaseModel
from typing import Optional, Literal



def get_canvas():
    """
    Helper function to create and return a Canvas API client instance.

    Returns:
        Canvas: An authenticated Canvas API client instance.

    Note:
        Requires CANVAS_API_URL and CANVAS_API_TOKEN environment variables to be set.
    """
    url = os.getenv('CANVAS_API_URL')
    token = os.getenv('CANVAS_API_TOKEN')
    return Canvas(url, token)
