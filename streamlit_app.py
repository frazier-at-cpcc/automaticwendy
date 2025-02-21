import asyncio
import streamlit as st
from scraper import CourseScraper
from ui import UI

async def main():
    """Main application entry point."""
    # Setup UI
    UI.setup_page()
    UI.install_playwright_browsers()
    
    # Get credentials
    email, password = UI.get_credentials()
    
    if not st.button("Fetch Course Schedules"):
        return
        
    if not email or not password:
        UI.show_error("Please enter both email and password")
        return
    
    # Create progress indicators
    progress_bar, status_text = UI.create_progress_indicators()
    
    try:
        async with CourseScraper() as scraper:
            df = await scraper.scrape_all_courses(
                email,
                password,
                progress_callback=progress_bar.progress,
                status_callback=lambda msg: setattr(status_text, 'text', msg)
            )
            
            # Display results
            UI.display_results(df)
            
    except Exception as e:
        UI.show_error(str(e))
        
    finally:
        UI.clear_progress_indicators(progress_bar, status_text)

if __name__ == "__main__":
    asyncio.run(main())