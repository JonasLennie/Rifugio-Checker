import pdfplumber
import numpy as np
import requests

def get_available_nights(pdf_path, start_date=12, end_date=21, target_month="September"):
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
                                # Check text availability
                                text_avail = avail and avail.strip() and avail.strip() != '1'
                                
                                # Check color availability
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

url = "https://www.rifugiopiandicengia.it/CustomerData/764/Files/Documents/verfuegbarkeiten.pdf"
path = 'tmp.pdf'
response = requests.get(url, timeout=30)
with open(path, 'wb') as f:
    f.write(response.content)

result = get_available_nights(path)
print(result)