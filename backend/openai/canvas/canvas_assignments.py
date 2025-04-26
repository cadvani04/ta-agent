"""
Delete an assignment**
List assignments**
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

