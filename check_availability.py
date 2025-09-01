import pdfplumber
import numpy as np
import requests
import os

def get_available_nights(pdf_path, start_date=9, end_date=21, target_month="September"):
    available_nights = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            im = page.within_bbox((0, 0, page.width, page.height)).to_image()
            pil_image = im.original
            
            for i, table in enumerate(page.extract_tables()):
                if table and len(table) >= 4:
                    month = table[0][0].split('/')[0].strip()
                    if month != target_month:
                        continue
                        
                    days = table[1]
                    dates = table[2]
                    availability = table[3]
                    
                    table_bbox = page.find_tables()[i].bbox
                    cell_width = (table_bbox[2] - table_bbox[0]) / len(dates)
                    row_height = (table_bbox[3] - table_bbox[1]) / len(table)
                    
                    for j, (day, date, avail) in enumerate(zip(days, dates, availability)):
                        try:
                            date_num = int(date)
                            if start_date <= date_num <= end_date:
                                text_avail = avail and avail.strip() and avail.strip() != '1'
                                
                                x0 = table_bbox[0] + j * cell_width
                                x1 = x0 + cell_width
                                y0 = table_bbox[1] + 3 * row_height
                                y1 = y0 + row_height
                                
                                cell_im = pil_image.crop((x0, y0, x1, y1))
                                avg_color = np.array(cell_im).mean(axis=(0,1))
                                is_green = avg_color[1] > avg_color[0] and avg_color[1] > avg_color[2]
                                
                                if text_avail or (is_green and not (avail and avail.strip())):
                                    available_nights.append(f"{day} {date} {month}")
                        except ValueError:
                            continue
    
    return available_nights

def get_open_issues():
    """Get all open issues with availability-alert label"""
    token = os.environ.get('GITHUB_TOKEN')
    
    if not token:
        print("No GitHub token found, cannot check existing issues")
        return []
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    response = requests.get(
        f'https://api.github.com/repos/JonasLennie/Rifugio-Checker/issues?labels=availability-alert&state=open',
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get issues: {response.status_code}")
        return []

def extract_nights_from_issues(issues):
    """Extract nights mentioned in existing issue titles"""
    existing_nights = []
    for issue in issues:
        title = issue['title']
        # Look for nights in format "Wed 11 September" in the title
        import re
        nights = re.findall(r'[A-Za-z]+ \d+ [A-Za-z]+', title)
        existing_nights.extend(nights)
    return existing_nights

def create_issue(title, body):
    """Create a GitHub issue for notification"""
    token = os.environ.get('GITHUB_TOKEN')
    
    if not token:
        print("No GitHub token found, skipping issue creation")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',  # Changed from 'token' to 'Bearer'
        'Accept': 'application/vnd.github+json',  # Updated accept header
        'X-GitHub-Api-Version': '2022-11-28'  # Added version header
    }
    
    data = {
        'title': title,
        'body': body,
        'labels': ['availability-alert'],
        'assignees': ['miberl']
    }
    
    response = requests.post(
        f'https://api.github.com/repos/JonasLennie/Rifugio-Checker/issues',
        headers=headers,
        json=data
    )
    
    if response.status_code == 201:
        print(f"Issue created: {response.json()['html_url']}")
    else:
        print(f"Failed to create issue: {response.status_code}")
        print(f"Response: {response.text}")

def main():
    url = "https://www.rifugiopiandicengia.it/CustomerData/764/Files/Documents/verfuegbarkeiten.pdf"
    pdf_path = 'tmp.pdf'
    
    # Download PDF
    response = requests.get(url, timeout=30)
    with open(pdf_path, 'wb') as f:
        f.write(response.content)
    
    # Get current availability
    current_availability = get_available_nights(pdf_path)
    print(f"Current availability: {current_availability}")
    
    # Get existing issues and extract nights already reported
    open_issues = get_open_issues()
    previous_availability = extract_nights_from_issues(open_issues)
    print(f"Previously reported nights: {previous_availability}")
    
    # Check for new availability
    new_nights = [night for night in current_availability if night not in previous_availability]
    
    if new_nights:
        # Create title with specific nights
        nights_str = ', '.join(new_nights)
        title = f"🏔️ New Rifugio Availability: {nights_str}"
        
        body = f"""New availability detected:

**New nights available:**
{chr(10).join(f'• {night}' for night in new_nights)}

**All currently available nights:**
{chr(10).join(f'• {night}' for night in current_availability)}

**PDF Source:** {url}

Check the rifugio website for booking: https://www.rifugiopiandicengia.it/"""
        
        create_issue(title, body)
        print(f"New availability found: {new_nights}")
    else:
        print("No new availability")
    
    # Clean up
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

if __name__ == "__main__":
    main()