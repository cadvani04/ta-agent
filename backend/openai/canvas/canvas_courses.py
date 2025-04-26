# https://canvas.instructure.com/doc/api/courses.html#method.courses.create_file
from openai_tools import *
# —————————————————————————————
# Account endpoints
# —————————————————————————————


# —————————————————————————————
# Course endpoints
# —————————————————————————————

# TODO (low prio): IMPLEMENT ADD_COURSE (CURRENTLY CAN'T BC OF ADMIN LIMITATIONS)

# TODO (medium prio): IMPLEMENT UPLOAD_FILE (it's a longer process) (https://canvas.instructure.com/doc/api/file.file_uploads.html#method.file_uploads.url)
@function_tool()
def upload_file(course_id: int):
    pass

"""
full list:
List recently logged in students**
Get single user**
Search for content share users
Preview processed html
Course activity stream
Course activity stream summary**
Course TODO items** (not sure, if it's what i think it is then it is important)
Delete/Conclude a course**
Get course settings
Update course settings
Return test student for course
Get a single course**
Update a course**
Update courses
Reset a course**
Get effective due dates**
Permissions
Get bulk user progress
Remove quiz migration alert
Get course copy status
Copy course content
"""

@function_tool()
def get_all_courses():
    """
    Get a list of all courses available to the authenticated user.

    Returns:
        list: A list of dictionaries containing course IDs and names and account_ids.

    Raises:
        HTTPException: If there's an API error.
    """
    canvas = get_canvas()
    return [{"id": c.id, "name": c.name, "account_id": c.account_id, "root_account_id": c.root_account_id} for c in canvas.get_courses()]

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