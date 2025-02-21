from typing import List, Dict, Optional
import os
from playwright.async_api import async_playwright, Browser, Page
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
from config import BROWSER_CONFIG, CHROME_PATHS, BASE_URL, COURSES_URL, SELECTORS, COLUMNS

class BrowserManager:
    @staticmethod
    async def initialize_browser() -> Browser:
        """Initialize and return a browser instance."""
        async with async_playwright() as playwright:
            try:
                return await playwright.chromium.launch(**BROWSER_CONFIG)
            except Exception as e:
                # Try alternative browser configurations
                executable_path = BrowserManager._find_browser_executable()
                if not executable_path:
                    raise RuntimeError("No suitable browser executable found")
                
                return await playwright.chromium.launch(
                    **BROWSER_CONFIG,
                    executable_path=executable_path
                )
    
    @staticmethod
    def _find_browser_executable() -> Optional[str]:
        """Find a suitable browser executable on the system."""
        return next((path for path in CHROME_PATHS if os.path.exists(path)), None)

class CourseScraper:
    def __init__(self, browser: Browser):
        self.browser = browser
    
    @staticmethod
    def extract_course_code(title: str) -> str:
        """Extract course code from course title."""
        import re
        match = re.match(r'^([^:]+):', title)
        return match.group(1).strip() if match else ''

    async def login(self, page: Page, email: str, password: str) -> None:
        """Log in to Epic Learning Network."""
        await page.goto(BASE_URL)
        await page.get_by_role("textbox", name="Email").fill(email)
        await page.get_by_role("textbox", name="Password").fill(password)
        await page.get_by_role("textbox", name="Password").press("Enter")
        
    async def get_course_links(self, page: Page) -> tuple[List[str], List[str]]:
        """Get all course links and names from the courses page."""
        await page.goto(COURSES_URL)
        courses_html = await page.content()
        soup = BeautifulSoup(courses_html, 'html.parser')
        
        course_links = []
        course_names = []
        for row in soup.find_all('tr', class_=SELECTORS['course_info']):
            title_cell = row.find('td', class_=SELECTORS['course_title'])
            if title_cell and title_cell.find('a'):
                link = title_cell.find('a')['href']
                name = title_cell.text.strip()
                course_links.append(link)
                course_names.append(name)
        
        return course_links, course_names

    async def parse_class_schedule(self, html_content: str, course_title: str) -> List[Dict]:
        """Parse class schedule from course page HTML."""
        course_code = self.extract_course_code(course_title)
        soup = BeautifulSoup(html_content, 'html.parser')
        schedule_table = soup.find('table', class_=SELECTORS['course_table'])
        classes_data = []
        
        if schedule_table:
            rows = schedule_table.find_all('tr', class_=SELECTORS['course_row'])
            for row in rows:
                partner = row.find('td', class_='course-lp-partner')
                if not partner or partner.text.strip() != "Fast Lane US":
                    continue
                
                class_data = {
                    'Course Code': course_code,
                    'Course Title': course_title,
                    'Partner': "Fast Lane US"
                }
                
                # Extract all other fields
                fields = {
                    'Start Date': 'course-lp-date',
                    'Start Time': 'course-lp-time',
                    'Days': 'course-lp-days',
                    'Status': 'course-lp-status',
                    'Retail Price': 'course-lp-price',
                    'Epic Price': 'course-lp-partner-price',
                    'CW Included': 'course-lp-cw-included',
                    'Last Updated': 'course-lp-last-updated',
                    'Student Count': 'course-lp-students'
                }
                
                for field, css_class in fields.items():
                    element = row.find('td', class_=css_class)
                    class_data[field] = element.text.strip() if element else ''
                
                # Handle registration link separately
                register_td = row.find('td', class_='course-lp-register')
                register_link = register_td.find('a') if register_td else None
                class_data['Registration Link'] = register_link['href'] if register_link else ''
                
                classes_data.append(class_data)
        
        return classes_data

    async def scrape_all_courses(
        self, 
        email: str, 
        password: str, 
        progress_callback: callable = None,
        status_callback: callable = None
    ) -> pd.DataFrame:
        """Scrape all course data and return as DataFrame."""
        async with await self.browser.new_context() as context:
            page = await context.new_page()
            
            try:
                if status_callback:
                    status_callback("Logging in to Epic Learning Network...")
                await self.login(page, email, password)
                
                if status_callback:
                    status_callback("Collecting course links...")
                course_links, course_names = await self.get_course_links(page)
                
                if status_callback:
                    status_callback(f"Found {len(course_links)} courses. Processing...")
                
                all_classes = []
                for i, (link, name) in enumerate(zip(course_links, course_names)):
                    await page.goto(link)
                    page_content = await page.content()
                    classes_data = await self.parse_class_schedule(page_content, name)
                    all_classes.extend(classes_data)
                    
                    if progress_callback:
                        progress = (i + 1) / len(course_links)
                        progress_callback(progress)
                    if status_callback:
                        status_callback(f"Processing course {i+1} of {len(course_links)}: {name}")
                
                return pd.DataFrame(all_classes)
                
            except Exception as e:
                raise RuntimeError(f"Scraping failed: {str(e)}") from e