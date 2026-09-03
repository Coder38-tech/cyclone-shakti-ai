import pdfplumber
import pandas as pd
import re

# 1. Replace with your actual PDF filename
PDF_FILENAME = "Preliminary_Tracks_2025.pdf"  # change to your exact file name
OUTPUT_CSV = "cyclone_shakhti_best_track.csv"

extracted_data = []
found_table = False

with pdfplumber.open("data2025.pdf") as pdf:
    for page_idx, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        
        # Look for Table 11
        if "Table 11" in text and "Shakhti" in text:
            found_table = True
            
        if found_table:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Clean line breaks and spaces inside table cells
                    cleaned = [re.sub(r'\s+', ' ', str(c)).strip() if c is not None else "" for c in row]
                    
                    # Ignore headers and blanks
                    if not any(cleaned) or "Date" in cleaned[0] or "Time" in cleaned[1]:
                        continue
                    
                    # Target valid observation rows (has numeric time like 0000, 0600, 1200)
                    if len(cleaned) >= 8 and any(re.match(r'^\d{4}$', item) for item in cleaned[:3]):
                        extracted_data.append(cleaned[:9])
                        
            # Stop when the next storm table starts
            if "Table 12" in text:
                break

if not extracted_data:
    print("Warning: Table 11 could not be detected automatically. Running fallback extraction on all tables...")
    # Fallback: Scans all pages for 8+ column data rows
    with pdfplumber.open("data2025.pdf") as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    cleaned = [re.sub(r'\s+', ' ', str(c)).strip() if c is not None else "" for c in row]
                    if len(cleaned) >= 8 and any(re.match(r'^\d{4}$', item) for item in cleaned[:3]):
                        extracted_data.append(cleaned[:9])

columns = ["Date", "Time_UTC", "Lat_N", "Long_E", "CI_No", "ECP_hPa", "Delta_P_hPa", "MSW_kt", "Category"]
df = pd.DataFrame(extracted_data, columns=columns)

# Forward-fill empty date cells
df["Date"] = df["Date"].replace("", None).ffill()

# Export clean CSV
df.to_csv(OUTPUT_CSV, index=False)
print(f"Success! Saved {len(df)} rows to {OUTPUT_CSV}")
print("\nFirst 5 rows:")
print(df.head())