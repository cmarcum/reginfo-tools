'''
This script provides full "Search of Regulatory Review" capability from the command-line
using python. It maps directly to the EO 12866 regulatory review search form at
https://www.reginfo.gov/public/do/eoAdvancedSearchMain (the "Reg Review" tab on reginfo.gov,
as opposed to the "ICR" tab that pra-icr-search.py targets).

Like pra-icr-search.py, this script automatically detects when the site's hard-coded 1000
result limit would be hit, and reactively chunks the search into monthly date-range blocks
so a single wide query doesn't just die. Unlike PRASearch, the EO Review results page offers
a genuine "View All" link (viewall=y) that returns every row of a sub-1000-result query in a
single response, so there is no need to walk paginated results page-by-page.

You can gracefully exit this script using ctrl+c.

Last updated: 9.20.2026
'''
import argparse
import requests
from bs4 import BeautifulSoup
import sys
import time
import csv
import re
from datetime import datetime, timedelta
import calendar

BASE_URL = "https://www.reginfo.gov"
SEARCH_MAIN_URL = f"{BASE_URL}/public/do/eoAdvancedSearchMain"
SEARCH_URL = f"{BASE_URL}/public/do/eoAdvancedSearch"

# The site paired these three independent date-range fields with three different "flavors"
# of search (received / concluded / published). If a wide query trips the 1000-result cap,
# we chunk by month using whichever pair the user actually supplied.
DATE_RANGE_FIELDS = [
    ("conclusionStartDate", "conclusionEndDate"),
    ("receivedStartDate", "receivedEndDate"),
    ("publishedStartDate", "publishedEndDate"),
]

EXPECTED_HEADERS = [
    "Received Date", "RIN", "Agency", "Rule Title", "Status",
    "Concluded Date", "Conclusion Action", "PubID", "RRID"
]

def parse_args():
    parser = argparse.ArgumentParser(description="Exact-mapped reactive scraper for RegInfo's EO 12866 Regulatory Review Search.")
    parser.add_argument('fields', nargs='*', help="Search fields as key=value pairs matching the HTML form (see eo-review-codebook.md). eoStatusCode=PR|CD is required by the server.")
    parser.add_argument('--output', default="reg_review_results.csv", help="Output CSV filename")
    parser.add_argument('--delay', type=int, default=2, help="Delay between chunked requests")
    return parser.parse_args()

def get_monthly_chunks(start_str, end_str):
    try:
        start_date = datetime.strptime(start_str, "%m/%d/%Y")
        end_date = datetime.strptime(end_str, "%m/%d/%Y")
    except ValueError:
        print("[!] Date format error. Ensure dates are strictly MM/DD/YYYY.")
        sys.exit(1)

    chunks = []
    current_start = start_date

    while current_start <= end_date:
        last_day = calendar.monthrange(current_start.year, current_start.month)[1]
        current_end = datetime(current_start.year, current_start.month, last_day)
        if current_end > end_date:
            current_end = end_date
        chunks.append((current_start.strftime("%m/%d/%Y"), current_end.strftime("%m/%d/%Y")))
        current_start = current_end + timedelta(days=1)

    return chunks

def find_date_range_pair(user_params):
    """Identify which of the three date-range field pairs the user actually populated."""
    for start_field, end_field in DATE_RANGE_FIELDS:
        if start_field in user_params and end_field in user_params:
            return start_field, end_field
    return None, None

def extract_rows(soup):
    """
    Locate the results table (identified by a header cell that reads exactly "RIN") and pull
    out each data row, plus the PubID/RIN pair (from the eAgendaViewRule link) and the RRID
    (from the eoDetails link, only present once a review has concluded). These two IDs are
    what reginfo-reg-download.py needs to pull the full rule record.
    """
    target_table = None
    for th in soup.find_all(['th', 'td']):
        if th.get_text(strip=True) == "RIN":
            target_table = th.find_parent('table')
            break

    if not target_table:
        tables = soup.find_all('table')
        if tables:
            target_table = max(tables, key=lambda t: len(t.find_all('tr')))

    if not target_table:
        return []

    rows = []
    for row in target_table.find_all('tr'):
        cols = row.find_all(['td', 'th'], recursive=False)
        if len(cols) < 7:
            continue
        texts = [c.get_text(strip=True) for c in cols]
        if texts[1] == "RIN" or "RIN" in texts[0]:
            continue  # header row

        pub_id, rrid = "", ""
        rin_link = cols[1].find('a', href=re.compile(r'eAgendaViewRule'))
        if rin_link:
            m = re.search(r'pubId=([^&]+)', rin_link.get('href', ''))
            if m:
                pub_id = m.group(1)
        status_link = cols[4].find('a', href=re.compile(r'eoDetails'))
        if status_link:
            m = re.search(r'rrid=(\d+)', status_link.get('href', ''))
            if m:
                rrid = m.group(1)

        rows.append(texts[:7] + [pub_id, rrid])

    return rows

def scrape_payload(session, user_params):
    """
    GET the search form first (establishes a session cookie the site's WAF expects on the
    following POST), then POST the query with ?viewall=y so the full result set (up to the
    1000-row cap) comes back in a single response - no pagination loop required.
    """
    try:
        session.get(SEARCH_MAIN_URL, timeout=15)
    except requests.exceptions.RequestException as e:
        print(f"  [!] Initial handshake failed: {e}")
        return "ERROR", []

    payload = {'autoRefresh': '1'}
    payload.update(user_params)
    payload.setdefault('sortBy', 'DESC')
    payload.setdefault('orderBy', 'OIRA_RECEIVED_DT')

    post_headers = session.headers.copy()
    post_headers['Content-Type'] = 'application/x-www-form-urlencoded'
    post_headers['Origin'] = BASE_URL
    post_headers['Referer'] = SEARCH_MAIN_URL

    try:
        response = session.post(f"{SEARCH_URL}?viewall=y", data=payload, headers=post_headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  [!] Error on search POST request: {e}")
        return "ERROR", []

    soup = BeautifulSoup(response.text, 'html.parser')
    page_text = soup.get_text(separator=' ')

    if re.search(r'allowed maximum number of results is 1000', page_text, re.IGNORECASE):
        return "LIMIT_EXCEEDED", []

    records_match = re.search(r'Number Of Records Found:\s*([\d,]+)', page_text, re.IGNORECASE)
    if not records_match:
        # The site silently redisplays the blank search form for zero-result / invalid queries.
        return "NO JOY", []

    total_records = int(records_match.group(1).replace(',', ''))
    print(f"  [*] Total Records Found: {total_records}")

    rows = extract_rows(soup)
    print(f"  [*] Extracted {len(rows)} rows.")

    if len(rows) > 0:
        return "SUCCESS", rows
    return "NO JOY", []

def main():
    args = parse_args()

    user_params = {}
    for field in args.fields:
        if '=' in field:
            key, val = field.split('=', 1)
            user_params[key] = val
        else:
            print(f"[!] Warning: Ignoring invalid field '{field}'. Use key=value.")

    if 'eoStatusCode' not in user_params:
        print("[!] Error: 'eoStatusCode' is required by reginfo.gov. Pass eoStatusCode=PR (Pending Review) or eoStatusCode=CD (Concluded).")
        sys.exit(1)

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    })

    all_master_results = [EXPECTED_HEADERS]

    try:
        print(f"[*] Attempting primary search: {user_params}")
        status, extracted_data = scrape_payload(session, user_params)

        if status == "LIMIT_EXCEEDED":
            print("[!] Query hit the 1000-record database limit.")
            start_field, end_field = find_date_range_pair(user_params)

            if start_field:
                print(f"[*] Automatically slicing query into monthly chunks using '{start_field}'/'{end_field}'...")
                date_chunks = get_monthly_chunks(user_params[start_field], user_params[end_field])

                for i, (chunk_start, chunk_end) in enumerate(date_chunks, 1):
                    print(f"\n[*] Processing Chunk {i}/{len(date_chunks)}: {chunk_start} to {chunk_end}")
                    chunk_params = user_params.copy()
                    chunk_params[start_field] = chunk_start
                    chunk_params[end_field] = chunk_end

                    if i > 1:
                        time.sleep(args.delay)

                    chunk_status, chunk_data = scrape_payload(session, chunk_params)
                    all_master_results.extend(chunk_data)

                    if chunk_status == "LIMIT_EXCEEDED":
                        print("  [!] WARNING: This month alone exceeded 1000 records. Data truncated; narrow your search criteria further.")
                    elif chunk_status == "SUCCESS":
                        print(f"  [+] Finalized Chunk {i}. Total chunk records: {len(chunk_data)}")
                    else:
                        print("  [-] No records found for this chunk.")
            else:
                print("[!] Cannot auto-chunk because no recognized date-range pair was provided.")
                print("[!] Add one of: conclusionStartDate/conclusionEndDate, receivedStartDate/receivedEndDate, or publishedStartDate/publishedEndDate (MM/DD/YYYY).")
        else:
            all_master_results.extend(extracted_data)
            if status == "SUCCESS":
                print(f"  [+] Search completed normally. Extracted {len(extracted_data)} total records.")
            else:
                print("[-] No records found for your query.")

    except KeyboardInterrupt:
        print("\n\n[!] Script manually interrupted by user (Ctrl+C)!")
        print("[!] Halting the scraper and saving the data collected so far...")

    total_records = len(all_master_results) - 1
    if total_records > 0:
        print(f"[*] Writing {total_records} TOTAL records to {args.output}...")
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(all_master_results)
        print("[*] Complete.")
    else:
        print("[-] CSV file was not created because no data were collected.")

if __name__ == "__main__":
    main()
