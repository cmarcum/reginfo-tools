"""
This script facilitates downloading the full public record for a single RIN (Regulation
Identifier Number) from the "regulation side" of reginfo.gov - the EO 12866 regulatory
review process - as a counterpart to pra-icr-download.py's ICR document downloader.

Unlike a PRA ICR, a rule under EO 12866 review doesn't have agency-uploaded "attachments"
sitting behind the record (the actual proposed/final rule text lives on federalregister.gov,
outside reginfo.gov). What reginfo.gov *does* host for a RIN, and what this script collects:

  1. Every "View Rule" snapshot of the RIN across Unified Agenda publication cycles
     (each edition of the agenda - pubId - gets its own eAgendaViewRule page), plus the
     machine-readable "RIN Data XML" export of each one.
  2. Every OIRA "Conclusion of EO 12866 Regulatory Review" record (eoDetails) once a
     given submission has concluded.
  3. Every EO 12866 meeting logged against the RIN, including any materials meeting
     requestors submitted - which download through the exact same downloadBtnOnClickHandler()
     JS shim that pra-icr-download.py already has to defeat, so that extraction logic is
     reused here verbatim.

Some code-blocks (extract_download_urls / download_file) are adapted directly from
pra-icr-download.py since reginfo.gov's document-download mechanism is identical on both
the ICR and Reg Review sides of the site.

Last updated: 9.20.2026
"""
import os
import argparse
import requests
from bs4 import BeautifulSoup
import sys
import re
import time
import json
import email.message
import mimetypes
from urllib.parse import urljoin

BASE_URL = "https://www.reginfo.gov"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"

def parse_args():
    parser = argparse.ArgumentParser(description="EO 12866 Regulatory Review RIN Downloader")
    parser.add_argument('rin', help="The RIN to pull (e.g., 2060-AW46)")
    parser.add_argument('--rule-data', action='store_true', help="Download View Rule snapshots + RIN Data XML for every agenda cycle the RIN appears in")
    parser.add_argument('--meetings', action='store_true', help="Download EO 12866 meeting records and any submitted meeting materials")
    parser.add_argument('--all', action='store_true', help="Download both rule data and meeting records")
    return parser.parse_args()

def find_review_history(session, rin):
    """
    reginfo.gov's EO Review Search requires an explicit eoStatusCode (PR or CD) - there is no
    "all statuses" option - so we query both to build the complete review history for a RIN.
    Returns a list of dicts: {receivedDate, status, pubId, rrid, concludedDate, action}.
    """
    history = []
    search_main = f"{BASE_URL}/public/do/eoAdvancedSearchMain"
    search_url = f"{BASE_URL}/public/do/eoAdvancedSearch"

    session.get(search_main, timeout=15)
    headers = session.headers.copy()
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    headers['Origin'] = BASE_URL
    headers['Referer'] = search_main

    for status in ('CD', 'PR'):
        payload = {'autoRefresh': '1', 'rin': rin, 'eoStatusCode': status, 'sortBy': 'DESC', 'orderBy': 'OIRA_RECEIVED_DT'}
        resp = session.post(f"{search_url}?viewall=y", data=payload, headers=headers, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')

        target_table = None
        for th in soup.find_all(['th', 'td']):
            if th.get_text(strip=True) == "RIN":
                target_table = th.find_parent('table')
                break
        if not target_table:
            continue

        for row in target_table.find_all('tr'):
            cols = row.find_all(['td', 'th'], recursive=False)
            if len(cols) < 7:
                continue
            texts = [c.get_text(strip=True) for c in cols]
            if texts[1] == "RIN":
                continue

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

            history.append({
                'receivedDate': texts[0], 'status': texts[4], 'concludedDate': texts[5],
                'action': texts[6], 'pubId': pub_id, 'rrid': rrid,
            })

    return history

def extract_download_urls(soup, base_url):
    """
    Identical in spirit to the helper of the same name in pra-icr-download.py: reginfo.gov
    hides real download links behind a handful of onclick JS shims rather than plain hrefs.
    """
    download_urls = set()

    for element in soup.find_all(['a', 'button', 'input']):
        href = element.get('href', '')
        onclick = element.get('onclick', '')

        if href and ('DownloadDocument' in href or 'Download' in href):
            download_urls.add(urljoin(base_url, href))

        js_code = href + onclick
        if js_code:
            match_handler = re.search(r'downloadBtnOnClickHandler\([\'"]([^\'"]+)[\'"]\)', js_code)
            if match_handler:
                download_urls.add(urljoin(base_url, match_handler.group(1)))
                continue

            match_doc = re.search(r'downloadDocument\([\'"]?(\d+)[\'"]?\)', js_code, re.IGNORECASE)
            if match_doc:
                doc_id = match_doc.group(1)
                download_urls.add(urljoin(base_url, f"/public/do/eoDownloadDocument?eodoc=true&documentID={doc_id}"))

    return list(download_urls)

def download_file(session, url, dest_dir):
    try:
        r = session.get(url, stream=True, timeout=20)
        r.raise_for_status()

        filename = None
        cd = r.headers.get('content-disposition')
        if cd:
            msg = email.message.EmailMessage()
            msg['content-disposition'] = cd
            filename = msg.get_filename()

        if not filename:
            content_type = r.headers.get('content-type', '').split(';')[0].strip()
            ext = mimetypes.guess_extension(content_type) or '.bin'
            filename = f"document_{int(time.time())}{ext}"

        filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
        base, ext = os.path.splitext(filename)
        counter = 1
        file_path = os.path.join(dest_dir, filename)
        while os.path.exists(file_path):
            filename = f"{base}_{counter}{ext}"
            file_path = os.path.join(dest_dir, filename)
            counter += 1

        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"    [+] Downloaded: {filename}")

    except requests.exceptions.RequestException as e:
        print(f"    [!] Failed to download: {url}\n        Error: {e}")

def download_rule_data(session, rin, pub_ids, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    for pub_id in sorted(set(p for p in pub_ids if p)):
        print(f"  [*] Fetching View Rule snapshot for pubId={pub_id}...")
        view_url = f"{BASE_URL}/public/do/eAgendaViewRule?pubId={pub_id}&RIN={rin}"
        try:
            resp = session.get(view_url, timeout=15)
            resp.raise_for_status()
            with open(os.path.join(dest_dir, f"ViewRule_{pub_id}.html"), 'w', encoding='utf-8') as f:
                f.write(resp.text)
            soup = BeautifulSoup(resp.text, 'html.parser')
            main = soup.find('div', class_='maincontent') or soup
            with open(os.path.join(dest_dir, f"ViewRule_{pub_id}.txt"), 'w', encoding='utf-8') as f:
                f.write(main.get_text('\n', strip=True))
        except requests.exceptions.RequestException as e:
            print(f"    [!] Failed to fetch View Rule for pubId={pub_id}: {e}")
            continue

        xml_url = f"{BASE_URL}/public/do/eAgendaViewRule?pubId={pub_id}&RIN={rin}&operation=OPERATION_EXPORT_XML"
        try:
            xml_resp = session.get(xml_url, timeout=15)
            xml_resp.raise_for_status()
            if xml_resp.text.strip().startswith('<?xml'):
                with open(os.path.join(dest_dir, f"RIN_Data_{pub_id}.xml"), 'w', encoding='utf-8') as f:
                    f.write(xml_resp.text)
                print(f"    [+] Saved RIN Data XML for pubId={pub_id}")
        except requests.exceptions.RequestException as e:
            print(f"    [!] Failed to fetch RIN Data XML for pubId={pub_id}: {e}")

def download_review_conclusions(session, rrids, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    for rrid in sorted(set(r for r in rrids if r)):
        print(f"  [*] Fetching review conclusion for rrid={rrid}...")
        url = f"{BASE_URL}/public/do/eoDetails?rrid={rrid}"
        try:
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            main = soup.find('div', class_='maincontent') or soup
            with open(os.path.join(dest_dir, f"Conclusion_{rrid}.txt"), 'w', encoding='utf-8') as f:
                f.write(main.get_text('\n', strip=True))
        except requests.exceptions.RequestException as e:
            print(f"    [!] Failed to fetch eoDetails for rrid={rrid}: {e}")

def download_meetings(session, rin, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    docs_dir = os.path.join(dest_dir, "Documents")

    print(f"  [*] Searching EO 12866 Meetings for RIN {rin}...")
    search_url = f"{BASE_URL}/public/do/eom12866SearchResults?rin={rin}"
    try:
        resp = session.get(search_url, timeout=15)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  [!] Failed to search EO 12866 Meetings: {e}")
        return

    soup = BeautifulSoup(resp.text, 'html.parser')
    meeting_links = set()
    for a in soup.find_all('a', href=re.compile(r'viewEO12866Meeting')):
        meeting_links.add(urljoin(BASE_URL, a.get('href')))

    if not meeting_links:
        print("  [-] No EO 12866 Meetings found for this RIN.")
        return

    print(f"  [*] Found {len(meeting_links)} meeting(s). Traversing...")
    meetings_summary = []
    for idx, meeting_url in enumerate(sorted(meeting_links), 1):
        time.sleep(1)
        try:
            m_resp = session.get(meeting_url, timeout=15)
            m_resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"    [!] Failed to fetch meeting page: {e}")
            continue

        m_soup = BeautifulSoup(m_resp.text, 'html.parser')
        main = m_soup.find('div', class_='maincontent') or m_soup
        meeting_id_match = re.search(r'meetingId=(\d+)', meeting_url)
        meeting_id = meeting_id_match.group(1) if meeting_id_match else str(idx)

        with open(os.path.join(dest_dir, f"Meeting_{meeting_id}.txt"), 'w', encoding='utf-8') as f:
            f.write(main.get_text('\n', strip=True))
        meetings_summary.append(meeting_url)

        doc_urls = extract_download_urls(m_soup, BASE_URL)
        if doc_urls:
            os.makedirs(docs_dir, exist_ok=True)
            print(f"      -> Meeting {meeting_id} has {len(doc_urls)} submitted document(s).")
            for d_url in doc_urls:
                download_file(session, d_url, docs_dir)

    with open(os.path.join(dest_dir, "meetings_index.json"), 'w', encoding='utf-8') as f:
        json.dump(meetings_summary, f, indent=2)

def main():
    args = parse_args()

    if args.all:
        args.rule_data = True
        args.meetings = True

    if not (args.rule_data or args.meetings):
        print("[!] Error: You must specify what to download:")
        print("[!] Add --rule-data, --meetings, or --all to your command.")
        sys.exit(1)

    rin = args.rin.upper()
    if not re.match(r'^\d{4}-[A-Z]{2}\d{2}$', rin):
        print(f"[!] Warning: '{rin}' does not strictly match the expected NNNN-AANN RIN format. Attempting anyway...")

    session = requests.Session()
    session.headers.update({
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': f"{BASE_URL}/public/do/eoAdvancedSearchMain",
    })

    master_dir = rin
    os.makedirs(master_dir, exist_ok=True)

    print(f"[*] Looking up review history for RIN {rin}...")
    history = find_review_history(session, rin)
    if not history:
        print("[-] No regulatory review records found for this RIN. Nothing to download.")
        sys.exit(0)

    with open(os.path.join(master_dir, "review_history.json"), 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)
    print(f"[*] Found {len(history)} review record(s) across the RIN's history.")

    if args.rule_data:
        print(f"\n[*] Downloading Rule Data for RIN {rin}...")
        pub_ids = [h['pubId'] for h in history]
        download_rule_data(session, rin, pub_ids, os.path.join(master_dir, "Rule_Data"))

        rrids = [h['rrid'] for h in history]
        if any(rrids):
            download_review_conclusions(session, rrids, os.path.join(master_dir, "Review_Conclusions"))

    if args.meetings:
        print(f"\n[*] Downloading EO 12866 Meetings for RIN {rin}...")
        download_meetings(session, rin, os.path.join(master_dir, "EO12866_Meetings"))

    print("\n[*] RIN record download complete.")

if __name__ == "__main__":
    main()
