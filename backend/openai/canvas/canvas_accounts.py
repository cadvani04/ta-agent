"""
List accounts**
Get accounts that admins can manage
Get accounts that users can create courses in
List accounts for course admins
Get a single account**
Settings
List environment settings
Permissions
Get the sub-accounts of an account
Get the Terms of Service
Get help links
Get the manually-created courses sub-account for the domain root account
List active courses in an accountUpdate an account
Delete a user from the root account
Restore a deleted user from a root account

need to implement 2!
"""
from openai_tools import *
def get_users(account_id: int):
    canvas = get_canvas()
    account = canvas.get_account(account_id)
    for user in account.get_users():
        print(user)
    # for att in account.attributes:
        # print(att)
    # print(account)
    
def get_account(account_id: int):
    canvas = get_canvas()
    account = canvas.get_account(account_id)
    return account