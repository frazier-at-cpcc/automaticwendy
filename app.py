import re
import csv
from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup


def extract_course_code(title):
    # Try to extract code from titles like "AWS-ADVDEV: Advanced Developing on AWS"
    match = re.match(r'^([^:]+):', title)
    if match:
        return match.group(1).strip()
    return ''


def parse_class_schedule(html_content, csv_writer, course_title):
    course_code = extract_course_code(course_title)
    soup = BeautifulSoup(html_content, 'html.parser')
    schedule_table = soup.find('table', class_='course-lp-table')
    classes_found = 0
    
    if schedule_table:
        rows = schedule_table.find_all('tr', class_='course-lp-info')
        for row in rows:
            partner = row.find('td', class_='course-lp-partner').text.strip() if row.find('td', class_='course-lp-partner') else ''
            
            # Only process Fast Lane US courses
            if partner == "Fast Lane US":
                classes_found += 1
                start_date = row.find('td', class_='course-lp-date').text.strip() if row.find('td', class_='course-lp-date') else ''
                start_time = row.find('td', class_='course-lp-time').text.strip() if row.find('td', class_='course-lp-time') else ''
                days = row.find('td', class_='course-lp-days').text.strip() if row.find('td', class_='course-lp-days') else ''
                status = row.find('td', class_='course-lp-status').text.strip() if row.find('td', class_='course-lp-status') else ''
                retail_price = row.find('td', class_='course-lp-price').text.strip() if row.find('td', class_='course-lp-price') else ''
                epic_price = row.find('td', class_='course-lp-partner-price').text.strip() if row.find('td', class_='course-lp-partner-price') else ''
                cw_included = row.find('td', class_='course-lp-cw-included').text.strip() if row.find('td', class_='course-lp-cw-included') else ''
                last_updated = row.find('td', class_='course-lp-last-updated').text.strip() if row.find('td', class_='course-lp-last-updated') else ''
                student_count = row.find('td', class_='course-lp-students').text.strip() if row.find('td', class_='course-lp-students') else ''
                register_link = row.find('td', class_='course-lp-register').find('a')['href'] if row.find('td', class_='course-lp-register') and row.find('td', class_='course-lp-register').find('a') else ''
                
                csv_writer.writerow([
                    course_code, course_title, start_date, start_time, partner, days, 
                    status, retail_price, epic_price, cw_included, last_updated, 
                    student_count, register_link
                ])
    
    print(f"  Found {classes_found} Fast Lane US classes for: {course_title}")
    return classes_found


def run(playwright: Playwright) -> None:
    print("Starting Epic Learning Network course scraper...")
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    # Login
    print("Logging in to Epic Learning Network...")
    page.goto("https://www.epiclearningnetwork.com/")
    page.get_by_role("textbox", name="Email").fill("salesoperations@fastlaneus.com")
    page.get_by_role("textbox", name="Email").press("Tab")
    page.get_by_role("textbox", name="Password").fill("FLUS2022")
    page.get_by_role("textbox", name="Password").press("Enter")
    print("Login successful")
    
    # First get all course links
    print("\nCollecting course links...")
    page.goto("https://www.epiclearningnetwork.com/courses/")
    courses_html = page.content()
    soup = BeautifulSoup(courses_html, 'html.parser')
    course_links = []
    course_names = []
    
    for row in soup.find_all('tr', class_='course-info'):
        title_cell = row.find('td', class_='course-title')
        if title_cell and title_cell.find('a'):
            link = title_cell.find('a')['href']
            name = title_cell.text.strip()
            course_links.append(link)
            course_names.append(name)
    
    print(f"Found {len(course_links)} total courses")
    
    # Create CSV file for class schedules
    total_classes = 0
    print("\nProcessing individual course pages...")
    with open('class_schedules.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow([
            'Course Code', 'Course Title', 'Start Date', 'Start Time', 'Partner', 
            'Days', 'Status', 'Retail Price', 'Epic Price', 'CW Included', 
            'Last Updated', 'Student Count', 'Registration Link'
        ])
        
        # Visit each course page and parse class schedule
        for link, name in zip(course_links, course_names):
            page.goto(link)
            page_content = page.content()
            classes_found = parse_class_schedule(page_content, writer, name)
            total_classes += classes_found

    print(f"\nScraping complete!")
    print(f"Total Fast Lane US classes found: {total_classes}")
    print(f"Results saved to: class_schedules.csv")

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
