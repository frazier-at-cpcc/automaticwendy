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
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Deploying to Streamlit Cloud

1. Push your code to GitHub
2. Connect your repository to Streamlit Cloud
3. Add the following to your Streamlit Cloud requirements:
   - No additional requirements needed, everything is in requirements.txt

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