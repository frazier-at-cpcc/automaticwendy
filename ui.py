from typing import Tuple, Optional
import streamlit as st
import pandas as pd
from config import APP_TITLE, APP_DESCRIPTION

class UI:
    @staticmethod
    def setup_page():
        """Configure the basic page settings."""
        st.set_page_config(page_title=APP_TITLE, layout="wide")
        st.title(APP_TITLE)
        st.write(APP_DESCRIPTION)
    
    @staticmethod
    def get_credentials() -> Tuple[str, str]:
        """Get user credentials from input fields."""
        email = st.text_input("Email", key="email")
        password = st.text_input("Password", type="password", key="password")
        return email, password
    
    @staticmethod
    def create_progress_indicators() -> Tuple[st.progress, st.empty]:
        """Create and return progress bar and status text containers."""
        return st.progress(0), st.empty()
    
    @staticmethod
    def display_results(df: pd.DataFrame):
        """Display the results dataframe and download button."""
        if len(df) > 0:
            st.success(f"Found {len(df)} Fast Lane US classes!")
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
    
    @staticmethod
    def show_error(error: str):
        """Display an error message."""
        st.error(f"An error occurred: {error}")
    
    @staticmethod
    def clear_progress_indicators(
        progress_bar: Optional[st.progress] = None, 
        status_text: Optional[st.empty] = None
    ):
        """Clear progress indicators from the UI."""
        if progress_bar:
            progress_bar.empty()
        if status_text:
            status_text.empty()

    @staticmethod
    def install_playwright_browsers():
        """Install Playwright browsers if not already installed."""
        import subprocess
        import sys
        
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