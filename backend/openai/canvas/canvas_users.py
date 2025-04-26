"""
List users in accounti
List the activity stream
Activity stream summary
List the TODO items
List counts for todo items
List upcoming assignments, calendar events
List Missing Submissions
Hide a stream item
Hide all stream items
Upload a file
Show user details
Create a user[DEPRECATED] 
Self register a user
Update user settings
Get custom colors
Get custom color
Update custom color
Update text editor preference
Get dashboard positions
Update dashboard positions
Edit a user
Terminate all user sessions
Log users out of all mobile apps
Merge user into another user
Split merged users into separate users
Get a Pandata Events jwt token and its expiration date
Get a users most recently graded submissions
Get user profile
List avatar options
List user page views
"""

from openai_tools import *

def get_user(user_id: int):
    # able to get the information about the user (name, sortable name) given the id
    canvas = get_canvas()
    canvas.get_user(0)
    canvas.get_user(user_id)
    user = canvas.get_user(user_id)
    print(f"User ID: {user.id}")
    print(f"Name: {user.name}")
    print(f"Sortable Name: {user.sortable_name}") 