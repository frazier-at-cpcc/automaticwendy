from typing import List, Dict

# Application configuration
APP_TITLE = "Epic Learning Network Course Scraper"
APP_DESCRIPTION = """
This app scrapes Fast Lane US course schedules from the Epic Learning Network.
Enter your credentials below to start.
"""

# URLs
BASE_URL = "https://www.epiclearningnetwork.com"
COURSES_URL = f"{BASE_URL}/courses/"

# Browser configuration
BROWSER_CONFIG = {
    "headless": True,
    "args": ["--no-sandbox"]
}

# System paths for Chrome/Chromium
CHROME_PATHS: List[str] = [
    '/usr/bin/chromium',          # Debian/Ubuntu
    '/usr/lib/chromium/chromium', # Alternative Debian path
    '/usr/bin/google-chrome',     # Chrome on Linux
]

# CSS Selectors and classes
SELECTORS = {
    "course_table": "course-lp-table",
    "course_row": "course-lp-info",
    "course_info": "course-info",
    "course_title": "course-title"
}

# Column definitions for the output DataFrame
COLUMNS: Dict[str, str] = {
    "Course Code": "course_code",
    "Course Title": "course_title",
    "Start Date": "start_date",
    "Start Time": "start_time",
    "Partner": "partner",
    "Days": "days",
    "Status": "status",
    "Retail Price": "retail_price",
    "Epic Price": "epic_price",
    "CW Included": "cw_included",
    "Last Updated": "last_updated",
    "Student Count": "student_count",
    "Registration Link": "register_link"
}