from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from canvasapi import Canvas
from agents import Agent, Runner, function_tool
from pydantic import BaseModel
from typing import Optional, Literal

from dotenv import load_dotenv

load_dotenv()

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# discord read, discord testing (agent)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/basic")
async def run():
    canvas = get_canvas()
    return [{"id": c.id, "name": c.name, "account_id": c.account_id, "root_account_id": c.root_account_id} for c in canvas.get_courses()]

@app.get("/list_courses")
def get_all_courses():
    canvas = get_canvas()
    return [{"id": c.id, "name": c.name, "account_id": c.account_id, "root_account_id": c.root_account_id} for c in canvas.get_courses()]

class CourseCreate(BaseModel):
    """
    Pydantic model for creating a new course in Canvas.

    All fields are optional except `name`; Canvas will default the name
    to "Unnamed Course" if you omit it.
    """
    name: str
    course_code: Optional[str] = None

    # Dates (ISO 8601). Ignored unless restrict_enrollments_to_course_dates=True
    start_at: Optional[str] = None # should be datetime
    end_at: Optional[str] = None
	# •	Datetime to string: use .strftime(format)
	# •	String to datetime: use datetime.strptime(string, format)
    # Licensing
    license: Optional[
        Literal[
            'private',
            'cc_by_nc_nd',
            'cc_by_nc_sa',
            'cc_by_nc',
            'cc_by_nd',
            'cc_by_sa',
            'cc_by',
            'public_domain'
        ]
    ] = None

    # Visibility
    is_public: Optional[bool] = None
    is_public_to_auth_users: Optional[bool] = None
    public_syllabus: Optional[bool] = None
    public_syllabus_to_auth: Optional[bool] = None
    public_description: Optional[str] = None

    # Wiki & forums
    allow_student_wiki_edits: Optional[bool] = None
    allow_wiki_comments: Optional[bool] = None
    allow_student_forum_attachments: Optional[bool] = None

    # Enrollment options
    open_enrollment: Optional[bool] = None
    self_enrollment: Optional[bool] = None
    restrict_enrollments_to_course_dates: Optional[bool] = None

    # SIS / integration identifiers
    term_id: Optional[str] = None
    sis_course_id: Optional[str] = None
    integration_id: Optional[str] = None

    # Grade settings
    hide_final_grades: Optional[bool] = None
    apply_assignment_group_weights: Optional[bool] = None

    # Time zone
    time_zone: Optional[str] = None  # e.g. "America/Los_Angeles"

    # Auto-enrollment & default view
    offer: Optional[bool] = None     # available immediately
    enroll_me: Optional[bool] = None # enroll creator as teacher
    default_view: Optional[
        Literal['feed', 'wiki', 'modules', 'syllabus', 'assignments']
    ] = None

    # Syllabus & grading
    syllabus_body: Optional[str] = None
    grading_standard_id: Optional[int] = None
    grade_passback_setting: Optional[Literal['nightly_sync', 'disabled', '']] = None

    # Course format
    course_format: Optional[Literal['on_campus', 'online', 'blended']] = None

    # Posting policy
    post_manually: Optional[bool] = None


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

@function_tool()
def add_course(course_data: CourseCreate):
    """
    Create a new course in Canvas.

    Args:
        course_data (CourseCreate): The course creation data.

    Returns:
        dict: A dictionary containing the created course's ID and name.

    Raises:
        HTTPException: If there's an API error during course creation.
    """
    canvas = get_canvas()
    new_course = canvas.create_course(course_data)
    return {"id": new_course.id, "name": new_course.name}

@function_tool()
def get_all_courses():
    """
    Get a list of all courses available to the authenticated user.

    Returns:
        list: A list of dictionaries containing course IDs and names.

    Raises:
        HTTPException: If there's an API error.
    """
    canvas = get_canvas()
    return [{"id": c.id, "name": c.name} for c in canvas.get_courses()]

@function_tool
def get_course(course_id: int):
    """
    Get details of a specific course by its ID.

    Args:
        course_id (int): The ID of the course to retrieve.

    Returns:
        dict: A dictionary containing the course's ID, name, start date, and end date.

    Raises:
        HTTPException: If the course is not found or there's an API error.
    """
    c = get_canvas().get_course(course_id)
    return {"id": c.id, "name": c.name, "start_at": c.start_at, "end_at": c.end_at}


agent = Agent(
    name="canvas-lms-agent",
    instructions=(
        "You are an assistant designed to help the user interact with the Canvas API. "
        "Your primary purpose is to perform actions in the Canvas API given the tools, "
        "and give information to the user based on what you can learn from querying "
        "the Canvas API and what they ask."
    ),
    tools=[get_all_courses, get_course],
    model="gpt-4o-mini",
)

print("agent init")

