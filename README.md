# PDF Availability Monitor

Automated monitoring system for tracking changes in refuge availability calendars with intelligent date-specific availability detection.

## Quick Start

1. **Configure GitHub Secrets:**
   ```
   EMAIL_FROM=your-email@gmail.com
   EMAIL_TO=notification-email@gmail.com  
   EMAIL_PASSWORD=your-app-password
   TARGET_DATES=2025-09-12,2025-09-21
   ```

2. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/rifugio_updates.git
   git push -u origin main
   ```

3. **The monitor will run automatically every 2 hours during business hours**

## Features

- 📄 **PDF Change Detection** - SHA256 hash comparison
- 🎯 **Date-Specific Analysis** - Focus on target dates (Sept 12-21)
- 🔄 **Multi-Method Analysis** - Text extraction, image analysis, OCR fallback
- 📧 **Rich Email Notifications** - HTML emails with availability status
- ⚡ **GitHub Actions Hosting** - Zero-cost automated monitoring
- 🔧 **Configurable** - Easy customization via YAML config

## How It Works

### Tier 1: Change Detection
- Downloads PDF every 2 hours
- Calculates SHA256 hash
- Compares with stored hash
- Sends basic "PDF updated" alert

### Tier 2: Smart Analysis
- **Method 1:** Text extraction (fastest, most reliable)
- **Method 2:** Image color analysis (fallback)
- **Method 3:** OCR + coordinate mapping (backup)

## Configuration

### Environment Variables (GitHub Secrets)
- `EMAIL_FROM` - Your Gmail address
- `EMAIL_TO` - Notification recipient
- `EMAIL_PASSWORD` - Gmail app password
- `TARGET_DATES` - Comma-separated dates (2025-09-12,2025-09-21)

### Gmail Setup
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the app password (not your regular password)

## Manual Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export EMAIL_FROM="your-email@gmail.com"
export EMAIL_TO="notification-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
export TARGET_DATES="2025-09-12,2025-09-21"

# Run monitor
cd src && python monitor.py
```

## File Structure

```
├── .github/workflows/
│   └── monitor.yml          # GitHub Actions workflow
├── src/
│   ├── monitor.py          # Main monitoring script
│   ├── pdf_analyzer.py     # PDF analysis methods
│   └── notifier.py         # Email notification system
├── data/
│   ├── last_hash.txt       # Stored PDF hash
│   └── availability.json   # Historical availability data
├── config/
│   └── settings.yml        # Configuration settings
├── requirements.txt        # Python dependencies
└── README.md
```

## Availability Status Legend

- 🟢 **Green** = Available for booking
- 🔴 **Red** = Fully booked
- 🟡 **Yellow** = Day use only  
- ⚪ **White** = Closed
- ❓ **Unknown** = Could not determine status

## Monitoring Schedule

- **Default:** Every 2 hours during business hours (8 AM - 8 PM CET)
- **Manual:** Use "Actions" tab in GitHub to trigger manually
- **Rate Limited:** Respectful of source server

## Troubleshooting

### Common Issues

1. **No emails received:**
   - Check spam folder
   - Verify Gmail app password
   - Check GitHub Actions logs

2. **Analysis always shows "unknown":**
   - PDF format may have changed
   - Check logs for specific errors
   - Try manual run for debugging

3. **Workflow fails:**
   - Verify all required secrets are set
   - Check Actions logs for error details

### Debugging

1. **View GitHub Actions logs:**
   - Go to "Actions" tab in your repository
   - Click on latest workflow run
   - Expand log sections to see details

2. **Local testing:**
   ```bash
   cd src
   python -c "
   from notifier import EmailNotifier
   notifier = EmailNotifier('from@email', 'to@email', 'password')
   print('✅ Connection OK' if notifier.test_email_connection() else '❌ Connection Failed')
   "
   ```

## Customization

### Different Target Dates
Update `TARGET_DATES` in GitHub Secrets:
```
TARGET_DATES=2025-10-01,2025-10-15
```

### Change Monitoring Frequency
Edit `.github/workflows/monitor.yml`:
```yaml
schedule:
  - cron: '0 */4 * * *'  # Every 4 hours
```

### Monitor Different PDF
Update `config/settings.yml`:
```yaml
pdf:
  url: "https://example.com/calendar.pdf"
```

## Support

This is a personal monitoring project. Issues and feature requests welcome via GitHub Issues.




| Juni / Giugno /June   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   |
|:----------------------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|
| So                    | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     |
| 1                     | 2      | 3      | 4      | 5      | 6      | 7      | 8      | 9      | 10     | 11     | 12     | 13     | 14     | 15     | 16     | 17     | 18     | 19     | 20     | 21     | 22     | 23     | 24     | 25     | 26     | 27     | 28     | 29     | 30     |
|                       |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |


| Juli / Luglio / July   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   |
|:-----------------------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|
| Di                     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     |
| 1                      | 2      | 3      | 4      | 5      | 6      | 7      | 8      | 9      | 10     | 11     | 12     | 13     | 14     | 15     | 16     | 17     | 18     | 19     | 20     | 21     | 22     | 23     | 24     | 25     | 26     | 27     | 28     | 29     | 30     | 31     |
|                        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |

| August / Agosto   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   |
|:------------------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|
| Fr                | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     |
| 1                 | 2      | 3      | 4      | 5      | 6      | 7      | 8      | 9      | 10     | 11     | 12     | 13     | 14     | 15     | 16     | 17     | 18     | 19     | 20     | 21     | 22     | 23     | 24     | 25     | 26     | 27     | 28     | 29     | 30     | 31     |
|                   |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |

| September / Settembre   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   |
|:------------------------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|
| Mo                      | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     |
| 1                       | 2      | 3      | 4      | 5      | 6      | 7      | 8      | 9      | 10     | 11     | 12     | 13     | 14     | 15     | 16     | 17     | 18     | 19     | 20     | 21     | 22     | 23     | 24     | 25     | 26     | 27     | 28     | 29     | 30     |
|                         |        |        |        |        |        |        |        |        |        | 1      |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        | 1      |        |        |        |

| Oktober / Ottobre   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   | None   |
|:--------------------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|
| Mi                  | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     | Sa     | So     | Mo     | Di     | Mi     | Do     | Fr     |
| 1                   | 2      | 3      | 4      | 5      | 6      | 7      | 8      | 9      | 10     | 11     | 12     | 13     | 14     | 15     | 16     | 17     | 18     | 19     | 20     | 21     | 22     | 23     | 24     | 25     | 26     | 27     | 28     | 29     | 30     | 31     |
|                     |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |        |