"""
Get department-level participation data
Get department-level grade data
Get department-level statistics
Get department-level statistics, broken down by subaccount
Get course-level participation data**
Get course-level assignment data**
Get course-level student summary data**
Get user-in-a-course-level participation data*
Get user-in-a-course-level assignment data*
Get user-in-a-course-level messaging data*

3 for sure, last 3 are maybe.
"""
import os
import requests
from fastapi import HTTPException
from typing import Optional, Dict
from agents import function_tool

@function_tool()
def get_department_grades(
    account_id: int,
    term_id: Optional[int] = None,
    completed: bool = False
) -> Dict[int, int]:
    """
    Fetch the distribution of department‐level grades from Canvas Analytics.

    Args:
        account_id:   Canvas account ID for the department.
        term_id:      (Optional) If provided, fetch grades for that term.
        completed:    If True (and term_id is None), fetch the completed‐grades endpoint.
                      Otherwise (and term_id is None), fetch current‐grades.

    Returns:
        A dict mapping integer grade bins (0–100) to raw counts.

    Raises:
        HTTPException: on any non‐200 response from Canvas.
    """
    base = os.getenv("CANVAS_API_URL")  # e.g. "https://yourinstitution.instructure.com"
    token = os.getenv("CANVAS_API_TOKEN")
    if not base or not token:
        raise HTTPException(500, "Missing CANVAS_API_URL or CANVAS_API_TOKEN")

    # build URL
    if term_id is not None:
        url = f"{base}/api/v1/accounts/{account_id}/analytics/terms/{term_id}/grades"
    elif completed:
        url = f"{base}/api/v1/accounts/{account_id}/analytics/completed/grades"
    else:
        url = f"{base}/api/v1/accounts/{account_id}/analytics/current/grades"

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    if not resp.ok:
        raise HTTPException(resp.status_code, f"Canvas API error: {resp.text}")

    # The API returns a JSON object whose keys are strings "0"–"100"
    # and whose values are counts; convert keys to int
    raw = resp.json()
    return {int(bin_str): count for bin_str, count in raw.items()}
