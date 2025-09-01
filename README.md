# Rifugio Availability Checker

Automated system to monitor and notify about availability changes at Rifugio Pian di Cengia.

## Overview

This project monitors the availability PDF from [Rifugio Pian di Cengia](https://www.rifugiopiandicengia.it/) and automatically creates GitHub issues when new nights become available for booking.

## How It Works

1. **Downloads** the latest availability PDF from the rifugio's website
2. **Parses** the PDF to extract available nights in September (dates 9-21)
3. **Checks** existing GitHub issues to avoid duplicates
4. **Creates** new GitHub issues for newly available nights
5. **Includes** specific nights in the issue title and PDF source URL in the body

## Features

- ✅ Automated PDF parsing with visual analysis for green availability indicators
- ✅ GitHub issue creation with detailed availability information
- ✅ Duplicate prevention by checking existing open issues
- ✅ Specific night information in issue titles
- ✅ PDF source URL included in issue descriptions
- ✅ Automated workflow running every 30 minutes

## GitHub Workflow

The project includes a GitHub Actions workflow (`.github/workflows/check-availability.yml`) that:

- Runs every 30 minutes via cron schedule
- Can be triggered manually
- Uses Ubuntu latest with Python 3.11
- Installs required dependencies: `pdfplumber`, `numpy`, `requests`
- Has appropriate permissions for creating issues

## Configuration

### Required Environment Variables

- `GITHUB_TOKEN`: Automatically provided by GitHub Actions for issue creation

### Monitored Parameters

- **Date Range**: September 9-21
- **Target Month**: September
- **PDF Source**: `https://www.rifugiopiandicengia.it/CustomerData/764/Files/Documents/verfuegbarkeiten.pdf`

## Dependencies

- `pdfplumber`: PDF parsing and table extraction
- `numpy`: Image processing for color analysis
- `requests`: HTTP requests for PDF download and GitHub API
- `os`: Environment variable access
- `re`: Regular expression pattern matching

## Issue Format

Created issues follow this format:

**Title**: `🏔️ New Rifugio Availability: Wed 11 September, Thu 12 September`

**Body**:
```
New availability detected:

**New nights available:**
• Wed 11 September
• Thu 12 September

**All currently available nights:**
• Wed 11 September
• Thu 12 September
• Fri 13 September

**PDF Source:** https://www.rifugiopiandicengia.it/CustomerData/764/Files/Documents/verfuegbarkeiten.pdf

Check the rifugio website for booking: https://www.rifugiopiandicengia.it/
```

## Labels and Assignment

- **Labels**: `availability-alert`
- **Assignees**: `miberl`

## Manual Execution

To run the checker manually:

```bash
python check_availability.py
```

Make sure you have the required dependencies installed and `GITHUB_TOKEN` environment variable set.