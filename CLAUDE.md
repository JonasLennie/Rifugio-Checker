# Claude Development Notes

This file contains development commands and notes for maintaining the Rifugio Availability Checker.

## Development Commands

### Testing
```bash
python check_availability.py
```

### Dependencies Installation
```bash
pip install pdfplumber numpy requests
```

### Linting (if available)
```bash
# Add linting commands here when configured
```

## Code Structure

### Main Components

1. **`get_available_nights(pdf_path, start_date=9, end_date=21, target_month="September")`**
   - Parses PDF and extracts available nights
   - Uses both text and visual analysis (green color detection)
   - Returns list of available nights in format "Day Date Month"

2. **`get_open_issues()`**
   - Fetches open GitHub issues with `availability-alert` label
   - Returns JSON response from GitHub API

3. **`extract_nights_from_issues(issues)`**
   - Parses existing issue titles to extract already reported nights
   - Uses regex pattern `[A-Za-z]+ \d+ [A-Za-z]+` to match "Wed 11 September" format

4. **`create_issue(title, body)`**
   - Creates new GitHub issue with availability information
   - Assigns to `miberl` with `availability-alert` label

5. **`main()`**
   - Orchestrates the entire process
   - Downloads PDF, checks availability, compares with existing issues, creates new issues

## Recent Changes

- Replaced local JSON file state management with GitHub Issues API
- Added night-specific information in issue titles
- Included PDF source URL in issue body
- Improved duplicate detection by parsing existing issue titles

## API Integration

### GitHub API Usage
- **Authentication**: Bearer token via `GITHUB_TOKEN` environment variable
- **Endpoints**:
  - `GET /repos/JonasLennie/Rifugio-Checker/issues?labels=availability-alert&state=open`
  - `POST /repos/JonasLennie/Rifugio-Checker/issues`
- **Headers**: 
  - `Accept: application/vnd.github+json`
  - `X-GitHub-Api-Version: 2022-11-28`

### PDF Processing
- Downloads from: `https://www.rifugiopiandicengia.it/CustomerData/764/Files/Documents/verfuegbarkeiten.pdf`
- Uses `pdfplumber` for table extraction
- Performs color analysis on table cells to detect green availability indicators
- Filters for September dates 9-21

## Error Handling

- GitHub token validation
- HTTP response status checking
- PDF parsing error handling for invalid date formats
- File cleanup (temporary PDF removal)

## Workflow Integration

- Runs every 30 minutes via GitHub Actions cron
- Manual trigger available via `workflow_dispatch`
- Uses Ubuntu latest with Python 3.11
- Requires `issues: write` and `contents: read` permissions