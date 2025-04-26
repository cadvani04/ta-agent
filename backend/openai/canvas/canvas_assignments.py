"""
Delete an assignment**
Get assignments**
List assignments for user**
Duplicate assignment
List group members for a student on an assignment**
Get a single assignment**
Create an assignment**
Edit an assignment**
Bulk update assignment dates


List assignment overrides
Get a single assignment override
Redirect to the assignment override for a group
Redirect to the assignment override for a section
Create an assignment override
Update an assignment override
Delete an assignment override
Batch retrieve overrides in a course
Batch create overrides in a course
Batch update overrides in a course

8 to implement
"""
from openai_tools import *

class AssignmentCreate(BaseModel):
    """
    Pydantic model for creating a new assignment in Canvas.
    All fields are strings (ISO-8601 for dates), lists of strings, or string literals.
    """
    name: str  # Required

    position: Optional[str] = None
    submission_types: Optional[
        List[
            Literal[
                "online_quiz", "none", "on_paper", "discussion_topic",
                "external_tool", "online_upload", "online_text_entry",
                "online_url", "media_recording", "student_annotation"
            ]
        ]
    ] = None
    allowed_extensions: Optional[List[str]] = None

    turnitin_enabled: Optional[str] = None
    vericite_enabled: Optional[str] = None
    turnitin_settings: Optional[str] = None

    integration_data: Optional[str] = None
    integration_id: Optional[str] = None

    peer_reviews: Optional[str] = None
    automatic_peer_reviews: Optional[str] = None
    notify_of_update: Optional[str] = None

    group_category_id: Optional[str] = None
    grade_group_students_individually: Optional[str] = None

    external_tool_tag_attributes: Optional[str] = None

    points_possible: Optional[str] = None
    grading_type: Optional[
        Literal["pass_fail", "percent", "letter_grade", "gpa_scale", "points", "not_graded"]
    ] = None

    due_at: Optional[str] = None
    lock_at: Optional[str] = None
    unlock_at: Optional[str] = None

    description: Optional[str] = None
    assignment_group_id: Optional[str] = None
    assignment_overrides: Optional[str] = None

    only_visible_to_overrides: Optional[str] = None
    published: Optional[str] = None

    grading_standard_id: Optional[str] = None
    omit_from_final_grade: Optional[str] = None
    hide_in_gradebook: Optional[str] = None

    quiz_lti: Optional[str] = None

    moderated_grading: Optional[str] = None
    grader_count: Optional[str] = None
    final_grader_id: Optional[str] = None
    grader_comments_visible_to_graders: Optional[str] = None
    graders_anonymous_to_graders: Optional[str] = None
    graders_names_visible_to_final_grader: Optional[str] = None

    anonymous_grading: Optional[str] = None
    allowed_attempts: Optional[str] = None
    annotatable_attachment_id: Optional[str] = None

class AssignmentEdit(AssignmentCreate):
    name: Optional[str] = None  # just override this one field

@function_tool()
def create_assignment(course_id: int, assignment_data: AssignmentCreate):
    """
    Create a new assignment in the specified Canvas course.

    This tool uses the Canvas Python client to add an assignment with the given parameters
    to the course identified by `course_id`. The `assignment_data` must be an instance of
    the `AssignmentCreate` Pydantic model, containing at minimum the required `name` field
    and any optional settings (e.g., `points_possible`, `due_at`, `submission_types`, etc.). The `name` field is required.

    Args:
        assignment_data (AssignmentCreate):
            A Pydantic model instance whose attributes map directly to the Canvas API’s
            `assignment[...]` parameters.

    Returns:
        str:
            A confirmation message: `"Successfully created assignment."`

    Raises:
        KeyError:
            If the course cannot be found or if required assignment fields are missing
            or invalid.
    """
    try:
        canvas = get_canvas()
        course = canvas.get_course(course_id)
        payload = assignment_data.model_dump(exclude_none=True)
        course.create_assignment(payload)
        return "Successfully created assignment."
    except KeyError:
        raise KeyError("Problem in create_assignment.")

@function_tool()
def get_assignments(course_id: int):
    """
    Retrieve all assignments for a specific Canvas course in a structured format.

    This function fetches every assignment in a course and returns a clean, simplified 
    list of dictionaries containing the most important details for each assignment, 
    such as its name, description, due date, points possible, type of assignment, 
    and publication status.

    Args:
        course_id (int): The Canvas course ID to fetch assignments from.

    Returns:
        List[Dict[str, Any]]: A list where each item represents an assignment, containing:
            - 'id' (int): Assignment ID
            - 'name' (str): Assignment name
            - 'description' (str): HTML description (if any)
            - 'due_at' (str or None): Due date in ISO 8601 format
            - 'points_possible' (float): Maximum points for the assignment
            - 'submission_types' (List[str]): List of allowed submission types
            - 'is_quiz_assignment' (bool): Whether the assignment is a quiz
            - 'published' (bool): Whether the assignment is visible to students
            - 'html_url' (str): URL to view the assignment in Canvas

    Raises:
        Exception: If fetching assignments fails.

    Notes:
        - Unpublished assignments are included in the results.
        - Some fields like `due_at` may be None if no due date is set.
    """
    canvas = get_canvas()
    assignments = canvas.get_course(course_id).get_assignments()

    formatted_assignments = []
    for asgn in assignments:
        formatted_assignments.append({
            "id": asgn.id,
            "name": asgn.name,
            "description": asgn.description,
            "due_at": asgn.due_at,  # ISO string or None
            "points_possible": asgn.points_possible,
            "submission_types": asgn.submission_types,
            "is_quiz_assignment": asgn.is_quiz_assignment,
            "published": asgn.published,
            "html_url": asgn.html_url,
        })

    return formatted_assignments

# @function_tool()
def edit_assignment(
    course_id: int,
    assignment_id: int,
    assignment_data: AssignmentEdit
) -> Dict[str, Any]:
    """
    Edit fields of an existing assignment in a Canvas course.

    This function updates only the provided fields on a Canvas assignment.  
    It fetches the specified assignment, applies all keys present in the  
    `assignment_data` Pydantic model, saves the changes via the API, and  
    returns a cleaned-up dictionary of the updated assignment.

    Args:
        course_id (int): The Canvas course ID containing the assignment.
        assignment_id (int): The ID of the assignment to update.
        assignment_data (AssignmentEdit): A Pydantic model containing only
            the fields to change. Possible fields include:
            - name (str): New name of the assignment
            - description (str): New HTML description
            - due_at (datetime or str): New due date (ISO 8601)
            - points_possible (float): New points possible
            - published (bool): Whether the assignment is visible to students
            - submission_types (List[str]): Allowed submission types
            (Any other updatable Canvas assignment field.)

    Returns:
        Dict[str, Any]: A dictionary representing the updated assignment,
        containing keys:
            - 'id' (int)
            - 'name' (str)
            - 'description' (str)
            - 'due_at' (str or None)
            - 'points_possible' (float)
            - 'submission_types' (List[str])
            - 'is_quiz_assignment' (bool)
            - 'published' (bool)
            - 'html_url' (str)

    Raises:
        Exception: If the API request fails when saving edits.
    """
    canvas = get_canvas()
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)

    # Build the payload from only the fields provided
    payload: Dict[str, Any] = {}
    for field_name, value in assignment_data.dict(exclude_unset=True).items():
        # Canvas API expects camelCase for some fields; adjust if needed
        payload[field_name] = value

    # Send the update request
    updated_asgn = assignment.edit(**payload)

    # Return a cleaned-up dict of the updated assignment
    return {
        "id": updated_asgn.id,
        "name": updated_asgn.name,
        "description": updated_asgn.description,
        "due_at": updated_asgn.due_at,
        "points_possible": updated_asgn.points_possible,
        "submission_types": updated_asgn.submission_types,
        "is_quiz_assignment": updated_asgn.is_quiz_assignment,
        "published": updated_asgn.published,
        "html_url": updated_asgn.html_url,
    }

    
    
def delete_assignment(assignment_id):
    pass
    