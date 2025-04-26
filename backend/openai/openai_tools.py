from canvasapi import Canvas
import os

# Initialize the Canvas object
# Replace 'your_canvas_url' with your Canvas instance's API URL (e.g., 'https://example.instructure.com')
# Replace 'your_api_token' with your Canvas API token


def add_course(canvas):
    pass


def delete_course(canvas, course_id):
    course = canvas.get_course(course_id)
    course.delete()


def get_all_courses(canvas):
    courses = canvas.get_courses()
    ret = ""
    for course in courses:
        ret += f"Course ID: {course.id}, Name: {course.name}\n"
    return ret


def create_assignment(canvas, course_id, assignment_name, **kwargs):
    """
    Create a new assignment in a course.

    :param canvas: The Canvas object initialized with API URL and token.
    :param course_id: The ID of the course where the assignment will be created.
    :param assignment_name: The name of the assignment.
    :param kwargs: Additional assignment details (e.g., due_at, points_possible, description).
    :return: The created Assignment object.
    """
    course = canvas.get_course(course_id)
    assignment = course.create_assignment({'name': assignment_name, **kwargs})
    return assignment


def delete_assignment(canvas, course_id, assignment_id):
    """
    Delete an assignment from a course.

    :param canvas: The Canvas object.
    :param course_id: The ID of the course containing the assignment.
    :param assignment_id: The ID of the assignment to delete.
    :return: True if the assignment was deleted successfully.
    """
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)
    assignment.delete()
    return True


def get_course_users(canvas, course_id):
    """
    Get a list of users enrolled in a course.

    :param canvas: The Canvas object.
    :param course_id: The ID of the course.
    :return: A list of User objects enrolled in the course.
    """
    course = canvas.get_course(course_id)
    users = course.get_users()
    return users


def get_course_files(canvas, course_id):
    """
    Get a list of files in a course.

    :param canvas: The Canvas object.
    :param course_id: The ID of the course.
    :return: A list of File objects in the course.
    """
    course = canvas.get_course(course_id)
    files = course.get_files()
    return files


def upload_file_to_folder(canvas, course_id, folder_path, file_path):
    """
    Upload a file to a specific folder in a course.

    :param canvas: The Canvas object.
    :param course_id: The ID of the course.
    :param folder_path: The full path of the folder (e.g., 'course files/Homeworks').
    :param file_path: The local path to the file to upload.
    :return: True if the file was uploaded successfully.
    """
    course = canvas.get_course(course_id)
    # Get all folders recursively
    folders = course.get_folders(recursive=True)
    # Find the target folder by its full_name
    target_folder = next(
        (f for f in folders if f.full_name == folder_path), None)
    if target_folder is None:
        raise ValueError(
            f"Folder '{folder_path}' not found in course {course_id}")
    # Upload the file
    with open(file_path, 'rb') as file:
        target_folder.upload(file)
    return True


def get_conversations(canvas):
    """
    Get a list of conversations for the current user.

    :param canvas: The Canvas object.
    :return: A list of Conversation objects.
    """
    conversations = canvas.get_conversations()
    return conversations


def get_course_assignments(canvas, course_id):
    """
    Get a list of assignments in a course.

    :param canvas: The Canvas object.
    :param course_id: The ID of the course.
    :return: A list of Assignment objects in the course.
    """
    course = canvas.get_course(course_id)
    assignments = course.get_assignments()
    return assignments


def get_assignment_submissions(canvas, course_id, assignment_id):
    """
    Get a list of submissions for an assignment.

    :param canvas: The Canvas object.
    :param course_id: The ID of the course.
    :param assignment_id: The ID of the assignment.
    :return: A list of Submission objects for the assignment.
    """
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)
    submissions = assignment.get_submissions()
    return submissions


def create_user(canvas, account_id, user_details):
    """
    Create a new user in an account.

    :param canvas: The Canvas object.
    :param account_id: The ID of the account where the user will be created.
    :param user_details: A dictionary with user details (e.g., {'name': 'John Doe'}).
    :return: The created User object.
    """
    account = canvas.get_account(account_id)
    user = account.create_user(user_details)
    return user


def enroll_user_in_course(canvas, course_id, user_id, enrollment_type):
    """
    Enroll a user in a course with a specific enrollment type.

    :param canvas: The Canvas object.
    :param course_id: The ID of the course.
    :param user_id: The ID of the user to enroll.
    :param enrollment_type: The type of enrollment (e.g., 'StudentEnrollment', 'TeacherEnrollment').
    :return: The Enrollment object.
    """
    course = canvas.get_course(course_id)
    enrollment = course.enroll_user(user_id, enrollment_type)
    return enrollment
