"""
This script facilitates downloading files associated with a 
 specific information collection request page from reginfo.gov.

Some code-blocks were generated using Google Gemini (as indicated in the comments).
 
Last updated: 2.27.2026

"""
import os
import argparse
import requests
from bs4 import BeautifulSoup
import sys
import re
import time
import email.message
import mimetypes
from urllib.parse import urljoin, urlparse, parse_qs

BASE_URL = "https://www.reginfo.gov"

def parse_args():
    parser = argparse.ArgumentParser(description="PRA ICR Attachment Downloader")
    parser.add_argument('ref_nbr', help="The ICR Reference Number (e.g., 202601-0920-012), or an OMB Control Number (e.g., 1121-0098) with --history")
    parser.add_argument('--collections', action='store_true', help="Download Collection Instruments")
    parser.add_argument('--supporting', action='store_true', help="Download Supporting Documents")
    parser.add_argument('--both', action='store_true', help="Download both sets of documents")
    parser.add_argument('--history', action='store_true', help="Treat ref_nbr as an OMB Control Number and download every ICR in its history")
    return parser.parse_args()

def get_history_refs(session, control_nbr):
    """
    Returns the ICR Reference Numbers listed on the OMB Control Number's history page
    (PRAOMBHistory), newest first, as reginfo.gov lists them, plus the Common Form (RCF)
    reference numbers on that page. RCF rows are other agencies' uses of a common form;
    they link to PRAViewRCF rather than PRAViewICR and are not downloaded.
    """
    hist_url = f"{BASE_URL}/public/do/PRAOMBHistory?ombControlNumber={control_nbr}"
    resp = session.get(hist_url, timeout=15)
    resp.raise_for_status()
    refs = []
    for ref in re.findall(r'PRAViewICR\?ref_nbr=(\d{6}-\d{4}-\d{3})', resp.text):
        if ref not in refs:
            refs.append(ref)
    rcf_refs = []
    for ref in re.findall(r'PRAViewRCF\?ref_nbr=([^"\'&\s<>]+)', resp.text):
        if ref not in rcf_refs:
            rcf_refs.append(ref)
    return refs, rcf_refs

def extract_download_urls(soup, base_url):
    """
    reginfo.gov and rocis are pretty out-dated as far as infrastructure goes and parsing of the JS and html tables 
    is needed to identify the direct download paths. This code-block was written using Google's Gemini and accomplishes that
    fairly seemlessly:
    """
    download_urls = set()
    
    for element in soup.find_all(['a', 'button', 'input']):
        href = element.get('href', '')
        onclick = element.get('onclick', '')
        
        if href and ('DownloadDocument' in href or 'Download' in href):
            full_url = urljoin(base_url, href)
            download_urls.add(full_url)
            
        js_code = href + onclick
        if js_code:
            match_handler = re.search(r'downloadBtnOnClickHandler\([\'"]([^\'"]+)[\'"]\)', js_code)
            if match_handler:
                url_path = match_handler.group(1)
                full_url = urljoin(base_url, url_path)
                download_urls.add(full_url)
                continue
                
            match_doc = re.search(r'downloadDocument\([\'"]?(\d+)[\'"]?\)', js_code, re.IGNORECASE)
            if match_doc:
                doc_id = match_doc.group(1)
                full_url = urljoin(base_url, f"/public/do/DownloadDocument?objectID={doc_id}")
                download_urls.add(full_url)
                
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
            
            parsed_url = urlparse(url)
            if 'objectID=' in url:
                oid = parse_qs(parsed_url.query).get('objectID', ['unknown'])[0]
                filename = f"document_{oid}{ext}"
            else:
                base_name = os.path.basename(parsed_url.path)
                if not base_name:
                    filename = f"downloaded_document_{int(time.time())}{ext}"
                else:
                    root, existing_ext = os.path.splitext(base_name)
                    filename = base_name if existing_ext else f"{base_name}{ext}"
            
        # Scrub filenames for better system compatibility
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
                
        print(f"  [+] Downloaded: {filename}")
        
    except requests.exceptions.RequestException as e:
        print(f"  [!] Failed to download: {url}\n      Error: {e}")

def download_icr(session, args, ref_nbr, master_dir):
    """
    Downloads the requested document sets for one ICR into master_dir.
    """
    
    # Get Supporting Documents
    if args.supporting:
        
        sup_dir = os.path.join(master_dir, "Supporting_Documents")
        os.makedirs(sup_dir, exist_ok=True)
        
        print(f"\n[*] Scanning Supporting Documents for ICR {ref_nbr}...")
        sup_url = f"{BASE_URL}/public/do/PRAViewDocument?ref_nbr={ref_nbr}"
        
        try:
            resp = session.get(sup_url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            downloads = extract_download_urls(soup, BASE_URL)
            if not downloads:
                print("  [-] No Supporting Documents found on this page.")
            else:
                print(f"  [*] Found {len(downloads)} Supporting Documents. Downloading...")
                for d_url in downloads:
                    download_file(session, d_url, sup_dir)
                    
        except requests.exceptions.RequestException as e:
            print(f"[!] Critical Error loading Supporting Documents page: {e}")

    # Information Collection Instrument Documents (with child-page traversal)
    """
    this code-chunk handles pagination and was written by Google's Gemini:
    """
    if args.collections:

        col_dir = os.path.join(master_dir, "Collection_Instruments")
        os.makedirs(col_dir, exist_ok=True)
        
        print(f"\n[*] Scanning Collection Instruments for ICR {ref_nbr}...")
        iclist_url = f"{BASE_URL}/public/do/PRAICList?ref_nbr={ref_nbr}"
        
        try:
            resp = session.get(iclist_url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            collection_downloads = set()
            collection_downloads.update(extract_download_urls(soup, BASE_URL))
            
            subpage_links = set()
            for a in soup.find_all('a'):
                href = a.get('href', '')
                if 'PRAViewIC' in href and 'icID=' in href:
                    subpage_links.add(urljoin(BASE_URL, href))
                    
            if subpage_links:
                print(f"  [*] Discovered {len(subpage_links)} distinct IC subpages. Traversing...")
                for idx, sub_url in enumerate(subpage_links, 1):
                    time.sleep(1) 
                    sub_resp = session.get(sub_url, timeout=15)
                    sub_soup = BeautifulSoup(sub_resp.text, 'html.parser')
                    
                    sub_downloads = extract_download_urls(sub_soup, BASE_URL)
                    print(f"      -> Subpage {idx}/{len(subpage_links)} contained {len(sub_downloads)} attachments.")
                    collection_downloads.update(sub_downloads)
                    
            if not collection_downloads:
                print("  [-] No Collection Instruments found.")
            else:
                print(f"  [*] Found {len(collection_downloads)} total Collection Instruments. Downloading...")
                for d_url in collection_downloads:
                    download_file(session, d_url, col_dir)
                    
        except requests.exceptions.RequestException as e:
            print(f"[!] Critical Error loading Collection Instruments page: {e}")

def main():
    args = parse_args()
    
    if args.both:
        args.collections = True
        args.supporting = True
        
    if not (args.collections or args.supporting):
        print("[!] Error: You must specify what to download: ")
        print("[!] Add --collections, --supporting, or --both to your command.")
        sys.exit(1)
        
    if args.history:
        if not re.match(r'^\d{4}-\d{4}$', args.ref_nbr):
            print(f"[!] Error: with --history, give an OMB Control Number like 1121-0098 (got '{args.ref_nbr}').")
            sys.exit(1)
    elif not re.match(r'^\d{6}-\d{4}-\d{3}$', args.ref_nbr):
        print(f"[!] Warning: '{args.ref_nbr}' does not strictly match the expected YYYYMM-XXXX-XXX format. Attempting anyway in case of some random legacy ICR or rocis bug (oy!)...")
        
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': f"{BASE_URL}/public/do/PRASearch"
    })
    
    if args.history:
        control_nbr = args.ref_nbr
        print(f"\n[*] Looking up the ICR history for OMB Control Number {control_nbr}...")
        try:
            refs, rcf_refs = get_history_refs(session, control_nbr)
        except requests.exceptions.RequestException as e:
            print(f"[!] Critical Error loading the history page: {e}")
            sys.exit(1)
        if not refs:
            print(f"[!] No ICRs found in the history for {control_nbr}.")
            sys.exit(1)
        if rcf_refs:
            print(f"[*] Skipping {len(rcf_refs)} Common Form (RCF) entries in the history. These are other agencies' uses of this common form; download one with its RCF reference number if you need it.")
        print(f"[*] Found {len(refs)} ICRs in the history. Downloading each into {control_nbr}/<ICR Reference Number>/ ...")
        for idx, ref in enumerate(refs, 1):
            print(f"\n[*] ICR {idx}/{len(refs)}: {ref}")
            download_icr(session, args, ref, os.path.join(control_nbr, ref))
            time.sleep(1)
    else:
        download_icr(session, args, args.ref_nbr, args.ref_nbr)

    print("\n[*] ICR file downloads complete.")

if __name__ == "__main__":
    main()
