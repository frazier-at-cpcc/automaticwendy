# Epic Learning Network Course Scraper

A Streamlit app that scrapes Fast Lane US course schedules from the Epic Learning Network.

## Features

- Secure credential input
- Real-time progress tracking
- Interactive data table display
- CSV download functionality
- Filters for Fast Lane US courses only

## Running Locally

1. Clone this repository
2. Install system dependencies (Linux/Ubuntu):
   ```bash
   sudo apt-get update
   sudo apt-get install chromium-browser chromium-driver
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```
5. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Deploying to Streamlit Cloud

1. Push your code to GitHub
2. Connect your repository to Streamlit Cloud
3. The deployment will automatically:
   - Install system dependencies from packages.txt
   - Install Python dependencies from requirements.txt
   - Install Playwright browser on startup

No additional configuration is needed as the app handles browser installation automatically.

## Project Structure

- `streamlit_app.py`: Main application code
- `requirements.txt`: Python package dependencies
- `packages.txt`: System dependencies for Streamlit Cloud
- `.gitignore`: Git ignore rules
- `README.md`: Documentation

## Usage

1. Enter your Epic Learning Network credentials
2. Click "Fetch Course Schedules"
3. Wait for the scraping to complete
4. View the results in the interactive table
5. Download the data as CSV if needed

## Security Note

- Credentials are never stored and are only used for the current session
- All communication is done securely over HTTPS
- No data is cached or saved on the server