import streamlit as st
import pandas as pd
import re
import asyncio
import subprocess
import sys
import os
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from io import StringIO

st.set_page_config(page_title="Epic Learning Network Course Scraper", layout="wide")

# Install playwright browsers on startup
if 'playwright_installed' not in st.session_state:
    try:
        st.info("Installing required browsers... This may take a moment.")
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            check=True
        )
        st.session_state.playwright_installed = True
        st.success("Browser installation complete!")
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to install browsers: {e.stderr.decode()}")
        st.stop()

def extract_course_code(title):
    match = re.match(r'^([^:]+):', title)
    if match:
        return match.group(1).strip()
    return ''

async def parse_class_schedule(html_content, course_title):
    course_code = extract_course_code(course_title)
    soup = BeautifulSoup(html_content, 'html.parser')
    schedule_table = soup.find('table', class_='course-lp-table')
    classes_data = []
    
    if schedule_table:
        rows = schedule_table.find_all('tr', class_='course-lp-info')
        for row in rows:
            partner = row.find('td', class_='course-lp-partner').text.strip() if row.find('td', class_='course-lp-partner') else ''
            
            # Only process Fast Lane US courses
            if partner == "Fast Lane US":
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
                
                classes_data.append({
                    'Course Code': course_code,
                    'Course Title': course_title,
                    'Start Date': start_date,
                    'Start Time': start_time,
                    'Partner': partner,
                    'Days': days,
                    'Status': status,
                    'Retail Price': retail_price,
                    'Epic Price': epic_price,
                    'CW Included': cw_included,
                    'Last Updated': last_updated,
                    'Student Count': student_count,
                    'Registration Link': register_link
                })
    
    return classes_data

async def scrape_courses(email, password, progress_bar, status_text):
    async with async_playwright() as playwright:
        try:
            # Try to launch browser with default configuration first
            browser = await playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox']  # Add no-sandbox argument for containerized environments
            )
        except Exception as e:
            st.error(f"Failed to launch browser with default configuration: {str(e)}")
            st.error("Attempting alternative launch configuration...")
            try:
                # Try to find the system Chrome/Chromium executable
                chrome_paths = [
                    '/usr/bin/chromium-browser',  # Ubuntu/Debian
                    '/usr/bin/chromium',          # Some Linux distros
                    '/usr/bin/google-chrome',     # Chrome on Linux
                ]
                
                executable_path = None
                for path in chrome_paths:
                    if os.path.exists(path):
                        executable_path = path
                        break
                
                if executable_path:
                    browser = await playwright.chromium.launch(
                        headless=True,
                        executable_path=executable_path,
                        args=['--no-sandbox']
                    )
                else:
                    raise Exception("No suitable browser executable found")
            except Exception as e:
                st.error(f"Failed to launch browser with all configurations: {str(e)}")
                raise Exception("Unable to launch browser. Please check system requirements.")
        
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Login
            status_text.text = "Logging in to Epic Learning Network..."
            await page.goto("https://www.epiclearningnetwork.com/")
            await page.get_by_role("textbox", name="Email").fill(email)
            await page.get_by_role("textbox", name="Email").press("Tab")
            await page.get_by_role("textbox", name="Password").fill(password)
            await page.get_by_role("textbox", name="Password").press("Enter")
            
            # Get course links
            status_text.text = "Collecting course links..."
            await page.goto("https://www.epiclearningnetwork.com/courses/")
            courses_html = await page.content()
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
            
            status_text.text = f"Found {len(course_links)} courses. Processing..."
            progress_bar.progress(0)
            
            all_classes = []
            for i, (link, name) in enumerate(zip(course_links, course_names)):
                await page.goto(link)
                page_content = await page.content()
                classes_data = await parse_class_schedule(page_content, name)
                all_classes.extend(classes_data)
                
                # Update progress
                progress = (i + 1) / len(course_links)
                progress_bar.progress(progress)
                status_text.text = f"Processing course {i+1} of {len(course_links)}: {name}"
            
            await browser.close()
            return pd.DataFrame(all_classes)
            
        except Exception as e:
            await browser.close()
            raise e

def main():
    st.title("Epic Learning Network Course Scraper")
    
    st.write("""
    This app scrapes Fast Lane US course schedules from the Epic Learning Network.
    Enter your credentials below to start.
    """)
    
    # Credential inputs
    email = st.text_input("Email", key="email")
    password = st.text_input("Password", type="password", key="password")
    
    if st.button("Fetch Course Schedules"):
        if not email or not password:
            st.error("Please enter both email and password")
            return
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            df = asyncio.run(scrape_courses(email, password, progress_bar, status_text))
            
            if len(df) > 0:
                st.success(f"Found {len(df)} Fast Lane US classes!")
                
                # Display the dataframe
                st.dataframe(df)
                
                # Create download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="class_schedules.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No Fast Lane US classes found")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            progress_bar.empty()
            status_text.empty()

if __name__ == "__main__":
    main()