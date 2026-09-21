# pra-icr-tools
Python scripts to help collect Paperwork Reduction Act Information Collections documents and metadata from reginfo.gov.

This repository contains Python tools designed to query, scrape, and download metadata and documents associated with information collection requests from the Office of Management and Budget's (OMB) Office of Information and Regulatory Affairs (OIRA) Paperwork Reduction Act (PRA) database [reginfo.gov](https://reginfo.gov). 

## Background

I wrote these scripts to support research, policy analysis, and the evaluation of federal data integrity by extracting comprehensive historical inventories and raw agency documents.

The reginfo.gov has an old, outdated techstack that is largely supported by a single individual in OIRA. It currently lacks a public-facing API and the site instead relies on deeply nested and often malformed HTML tables, fragile session states, hidden anti-forgery tokens, and document downloads that are obscured behind specific JavaScript triggers rather than standard URL hyperlinks. Because basic web scraping methods routinely fail against these structural idiosyncrasies extracting comprehensive historical inventories requires a custom-built approach. The tools developed here bypass these hurdles by programmatically intercepting and passing hidden form tokens to preserve state during complex pagination and utilizing a hybrid Document-Object Model (DOM) and regex to identify and retrieve files hidden behind legacy frontend code.

Currently, there are four python scripts in this repository, covering both halves of reginfo.gov:
* pra-icr-search.py creates a way to automagically pull search results from querying [PRASearch](https://www.reginfo.gov/public/do/PRASearch)
* pra-icr-download.py downloads documents from the ICR records pages in a reasonable file structure
* eo-reg-search.py does the same thing as pra-icr-search.py, but for the "Reg Review" side of the site - OMB/OIRA's [Search of Regulatory Review](https://www.reginfo.gov/public/do/eoAdvancedSearchMain) of rules under Executive Order 12866
* eo-reg-download.py pulls the full public record for a single RIN (Regulation Identifier Number) off the Reg Review side - View Rule snapshots, RIN Data XML, review conclusions, and any EO 12866 meeting materials
More details about each tool are provided below.

Several code-blocks were generated using Google's gemini (I've indicated in the script comments where that's the case). 

## Prerequisites
Ensure you have Python 3.7+ installed. Dependicies (mainly, [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) for access to it's great DOM handlers), are located in [requirements.txt](requirements.txt), which can be installed:
```bash
pip install -r requirements.txt
```

---

## Tool 1: PRA ICR Search (`pra-icr-search.py`)

### Description
A command-line headless scraper that maps directly to the RegInfo PRASearch form at [https://www.reginfo.gov/public/do/PRASearch](https://www.reginfo.gov/public/do/PRASearch). It automatically handles form tokens, complex pagination (including hybrid JavaScript triggers), and features a "Reactive Chunker" to work around the 1000 response limit that is hard-coded into reginfo.gov. If reginfo.gov rejects a query for exceeding its 1,000-result limit, the script intercepts the failure and automatically slices massive, multi-year queries into safe monthly blocks. 

It also features graceful interruption: pressing `Ctrl+C` will halt the scrape and securely save all data collected up to that exact moment.

Because the PRASearch relies on codes to indicate which agency or type of ICR (for example) as internal query elements, you should reference the [codebook](codebook.md) for help in writing search queries with this tool.

### Output
A single CSV file containing the tabular metadata for the requested Information Collection Requests (ICRs). Fields include: 


|`OMB Control No` | `Agency/Sub` | `Title` | `Request Type` | `Date Received` | `Concluded Date` | `Conclusion Action` | `Current Expiration Date` | `No. of ICs` | `No. of Forms`|
|-|-|-|-|-|-|-|-|-|-|

### Example Use Cases

**1. Track Federal Data Disconinuations**
Extract every single form that was discontinued government-wide during 2025. If this exceeds 1,000 records, the script will automatically chunk the timeline.
```bash
python pra-icr-search.py dateType=DI startDate=01/01/2025 endDate=12/31/2025 --output 2025_disruptions.csv --delay 2
```

**2. Evaluate Agency ICR activity over a fixed time period**
Pull a comprehensive history of the Environmental Protection Agency's concluded ICRs over a four-year span.
```bash
python pra-icr-search.py agencyCode=2000 dateType=CO startDate=01/01/2021 endDate=12/31/2024 --output epa_4_year_history.csv --delay 2
```

**3. Agency Active Inventory**
Pull all currently active forms for the IRS. This bypasses the chunker and leverages the bulletproof pagination handler to walk through dozens of pages.
```bash
python pra-icr-search.py agencyCode=1500 subAgencyCode=1545 icrStatus=AC --output irs_active_forms.csv --delay 2
```

**4. Track Emerging Collections**
Identify brand new forms (not extensions or revisions) currently sitting at OIRA awaiting initial approval.
```bash
python pra-icr-search.py icrStatus=RE requestType=RN --output new_collections_pending.csv --delay 2
```

---

## Tool 2: PRA ICR Downloader (`pra-icr-download.py`)

### Description
A document crawler that takes a specific ICR Reference Number and downloads all attached physical files (including collection instruments, subparts A and B, public comments, and more). Because agencies nest their actual surveys and forms deep within the site structure, this script automatically hunts for and traverses "child" subpages for Information Collection pages. 

It extracts native filenames from reginfo's `Content-Disposition` headers. If the server fails to provide a name, it dynamically infers the correct file extension based on the MIME type. The script also takes into account the fact that agencies are allowed to upload redundantly named files and handles file-name collisions by auto-incrementing duplicate filenames to ensure no redundant agency uploads are overwritten.

### Output
The script generates a parent directory named after the target ICR Reference Number. Depending on the command-line flags provided, it builds strictly named subdirectories (`Collection_Instruments` and/or `Supporting_Documents`) inside the parent folder, populated with the raw files (PDFs, Word docs, Excel sheets, etc.).

### Example Use Cases

**1. Download Everything (Collections and Supporting Documents)**
This example uses a recent CDC collection:
```bash
python pra-icr-download.py 202601-0920-012 --both
```

*Expected Output Structure:*
```text
202601-0920-012/
├── Collection_Instruments/
│   ├── Att_B_NOFO_DMP_20260113_FINAL_VERSION.pdf
│   └── ...
└── Supporting_Documents/
    ├── 30-Day_FRN_SSA_Data_Management_Plan_(DMP)_Template.docx
    └── ...
```

**2. Download Only the Collection Instruments**
```bash
python pra-icr-download.py 202601-0920-012 --collections
```

**3. Download Only Supporting Documents**
```bash
python pra-icr-download.py 202601-0920-012 --supporting
```

---

## Tool 3: EO 12866 Regulatory Review Search (`eo-reg-search.py`)

### Description
The regulation-side counterpart to `pra-icr-search.py`. It maps directly to the "Search of
Regulatory Review" form at [https://www.reginfo.gov/public/do/eoAdvancedSearchMain](https://www.reginfo.gov/public/do/eoAdvancedSearchMain) -
the search behind OMB/OIRA's review of agency rules under Executive Order 12866 (proposed
rules, final rules, and everything in between that crosses OIRA's desk before publication).

This search form is the same vintage as PRASearch and shares its 1000-result hard cap, so the
script carries over the same reactive monthly chunker. Unlike PRASearch, though, the EO Review
results page offers a genuine "View All" link, so under the 1000-row cap there's no pagination
loop to fight through - the whole result set comes back in one response.

Reginfo.gov silently rejects a query that omits `eoStatusCode` (Pending Review vs. Concluded)
by just redisplaying the blank search form, so the script requires it up front rather than
letting that fail invisibly. See [eo-review-codebook.md](eo-review-codebook.md) for the full
field and agency/sub-agency code reference.

### Output
A single CSV file with the tabular metadata for the matched rules. Fields include:

|`Received Date` | `RIN` | `Agency` | `Rule Title` | `Status` | `Concluded Date` | `Conclusion Action` | `PubID` | `RRID`|
|-|-|-|-|-|-|-|-|-|

`PubID` and `RRID` aren't shown on the results page itself - they're pulled out of the row's
links - but they're what `eo-reg-download.py` needs to go fetch the full rule record, so
the search tool surfaces them directly rather than making you re-derive them.

### Example Use Cases

**1. Pull a year of EPA's concluded reviews**
```bash
python eo-reg-search.py agencyCode=2000 eoStatusCode=CD conclusionStartDate=01/01/2024 conclusionEndDate=12/31/2024 --output epa_2024_concluded.csv --delay 2
```

**2. Everything currently sitting at OIRA**
```bash
python eo-reg-search.py eoStatusCode=PR --output pending_review.csv --delay 2
```

**3. Rules returned to an agency for reconsideration, government-wide**
```bash
python eo-reg-search.py eoStatusCode=CD concludedActionCode=RR conclusionStartDate=01/01/2000 conclusionEndDate=12/31/2024 --output returned_rules.csv --delay 2
```
If this exceeds 1,000 records, the script automatically slices the date range into monthly
blocks, same as `pra-icr-search.py` does for PRASearch.

**4. Full-text term search across rule titles/abstracts**
```bash
python eo-reg-search.py terms="artificial intelligence" eoStatusCode=CD --output ai_rules.csv --delay 2
```

---

## Tool 4: EO 12866 Regulatory Review RIN Downloader (`eo-reg-download.py`)

### Description
The regulation-side counterpart to `pra-icr-download.py`. A RIN under EO 12866 review doesn't
have agency-uploaded attachments sitting behind it the way an ICR does - the actual proposed
or final rule text is published on federalregister.gov, outside reginfo.gov. What reginfo.gov
*does* host for a RIN, and what this script collects into a per-RIN folder:

* Every "View Rule" snapshot of the RIN across Unified Agenda publication cycles (a RIN
  carried across multiple agenda editions gets a distinct snapshot each time), plus each
  snapshot's machine-readable RIN Data XML export.
* Every OIRA "Conclusion of EO 12866 Regulatory Review" record once a submission concludes.
* Every EO 12866 meeting logged against the RIN - including any materials meeting requestors
  submitted, which download through the exact same `downloadBtnOnClickHandler()` JS shim that
  `pra-icr-download.py` already has to defeat for ICR attachments.

Since reginfo.gov's EO Review search requires an explicit status (Pending Review vs.
Concluded) with no "search all statuses" option, the script queries both automatically to
assemble a RIN's complete review history before downloading anything.

### Output
The script generates a parent directory named after the RIN, containing:

```text
2060-AW46/
├── review_history.json
├── Rule_Data/
│   ├── ViewRule_202410.html
│   ├── ViewRule_202410.txt
│   ├── RIN_Data_202410.xml
│   ├── ViewRule_202504.html
│   ├── ViewRule_202504.txt
│   └── RIN_Data_202504.xml
├── Review_Conclusions/
│   ├── Conclusion_782011.txt
│   └── Conclusion_949811.txt
└── EO12866_Meetings/
    ├── meetings_index.json
    ├── Meeting_743873.txt
    ├── ...
    └── Documents/
        ├── 6.10.2025 OMB 2024 Extension Rule.pdf
        └── ...
```

### Example Use Cases

**1. Download Everything (Rule Data and Meetings)**
```bash
python eo-reg-download.py 2060-AW46 --all
```

**2. Download Only the Rule Data (View Rule snapshots, RIN Data XML, review conclusions)**
```bash
python eo-reg-download.py 2060-AW46 --rule-data
```

**3. Download Only EO 12866 Meeting Records and Materials**
```bash
python eo-reg-download.py 2060-AW46 --meetings
```
