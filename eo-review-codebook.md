# EO 12866 Regulatory Review Codebook

This codebook contains all the index codes mapping to the various parameters available on the
RegInfo.gov "Search of Regulatory Review" form (the "Reg Review" tab) available at:
[https://www.reginfo.gov/public/do/eoAdvancedSearchMain](https://www.reginfo.gov/public/do/eoAdvancedSearchMain).
This is the search behind OMB/OIRA's review of rules under Executive Order 12866 - the
regulation-side counterpart to the PRA Information Collection Review search documented in
[codebook.md](codebook.md).

These codes can be passed directly as `field=value` parameters to `reginfo-reg-search.py`.

## 0. Field Reference

| Field (`fieldName`) | Form Label | Type | Notes |
| :--- | :--- | :--- | :--- |
| `rin` | RIN | text | e.g. `2060-AW46` |
| `eoStatusCode` | Review Status | radio, **required** | `PR` (Pending Review) or `CD` (Concluded) - the server rejects a query silently (redisplays a blank form) if this is omitted |
| `agencyCode` | Agency | select | See §2 |
| `subAgencyCode` | Sub Agency | select | See §2 |
| `econSigs` | Economically Significant | checkbox | `Yes` / `No` |
| `terms` | Terms (Title and Abstract) | text | Free-text search of rule title/abstract |
| `s3f1Sigs` | Section 3(f)(1) Significant | checkbox | `Yes` / `No` |
| `legalDeadlines` | Legal Deadline | checkbox | `Judicial` / `Statutory` / `None` |
| `receivedStartDate` / `receivedEndDate` | Received Date Range | text (MM/DD/YYYY) | Date OIRA received the submission |
| `ruleStages` | Stage of Rulemaking | checkbox | See §1 |
| `healthcareFlag` | Affordable Care Act [Pub. L. 111-148 & 111-152] | checkbox | `Y` / `N` / `U` |
| `internationalFlag` | International Impacts | checkbox | `Y` / `N` / `X` (Uncollected) |
| `doddFrankFlag` | Dodd-Frank Wall Street Reform and Consumer Protection Act [Pub. L. 111-203] | checkbox | `Y` / `N` / `U` |
| `tcjaFlag` | Tax Cuts and Jobs Act [Pub. L. 115-97] | checkbox | `Y` / `N` / `X` (Uncollected) |
| `expeditedFlag` | (shown only when `tcjaFlag=Y`) | checkbox | `Y` / `N` |
| `covid19Flag` | Pandemic Response | checkbox | `Y` / `N` / `U` |
| `concludedActionCode` | Concluded Action | select | See §1 |
| `conclusionStartDate` / `conclusionEndDate` | (paired with Concluded Action) | text (MM/DD/YYYY) | Date OIRA concluded review |
| `majors` | Major | checkbox | `Y` / `N` |
| `publishedStartDate` / `publishedEndDate` | (Federal Register publication date) | text (MM/DD/YYYY) | |
| `federalisms` | Federalism | checkbox | `Y` / `N` / `U` |
| `homelandSecurities` | Related To Homeland Security | checkbox | `Y` / `N` / `U` |
| `smallEntities` | Small Entities Affected | checkbox | `G` (Governmental) / `B` (Businesses) / `O` (Organizations) / `N` / `U` |
| `unfundedMandates` | Unfunded Mandates | checkbox | `G` (Governmental) / `P` (Private) / `N` / `U` |
| `rfaRequires` | Regulatory Flexibility Analysis Required | checkbox | `G` (Governmental) / `B` (Businesses) / `O` (Organizations) / `N` / `U` |

A search needs at least one of `rin`, `terms`, or `agencyCode` to be meaningful to a human
(the site's own client-side JS enforces this before submit), but `reginfo-reg-search.py`
bypasses the browser entirely, so that rule is not actually enforced server-side - only
`eoStatusCode` is.

Checkbox fields accept multiple values in the live form (e.g. checking both Judicial and
Statutory legal deadlines); pass a comma-separated list to the script (e.g.
`legalDeadlines=Judicial,Statutory`) and it will be sent as repeated form fields.

## 1. Reg Review Function Index Codes

### Review Status (`eoStatusCode`)
| Code | Description |
| :--- | :--- |
| `PR` | Pending Review |
| `CD` | Concluded |

### Concluded Action (`concludedActionCode`)
| Code | Description |
| :--- | :--- |
| `CC` | Consistent with Change |
| `CW` | Consistent without Change |
| `EM` | Emergency |
| `EX` | Exempt from Executive Order |
| `IS` | Improperly Submitted |
| `RR` | Returned for Reconsideration |
| `SJ` | Statutory or Judicial Deadline |
| `SR` | Suspended Review |
| `WD` | Withdrawn |

### Stage of Rulemaking (`ruleStages`)
| Code | Description |
| :--- | :--- |
| `1` | Prerule |
| `2` | Proposed Rule |
| `3` | Interim Final Rule |
| `4` | Final Rule |
| `5` | Final Rule No Material Change |
| `6` | Notice |

## 2. Federal Agency & Sub-Agency Index Codes

Use the **Agency Code** for the `agencyCode` parameter, and the **Sub-Agency Code** for the
`subAgencyCode` parameter. These codes are shared with the PRA/ICR side of reginfo.gov (see
[codebook.md](codebook.md) §2), though not every agency that submits an ICR also has rules
reviewed under EO 12866, and vice versa - the list below is scoped to what the Reg Review
search form itself offers.

| Agency / Sub-Agency Name | Agency Code (`agencyCode`) | Sub-Agency Code (`subAgencyCode`) |
| :--- | :--- | :--- |
| **ACTION** | `3001` | |
| **Advisory Council on Historic Preservation** | `3010` | |
| **African Development Foundation** | `3005` | |
| **Agency for International Development** | `0412` | |
| **All** | `0000` | |
| **Appraisal Subcommittee of the FFIEC** | `3139` | |
| **Architectural and Transportation Barriers Compliance Board** | `3014` | |
| **Barry M. Goldwater Scholarship and Excellence in Education Foundation** | `3019` | |
| **Board of Directors of the HOPE for Homeowners Program** | `2580` | |
| **Civil Aeronautics Board** | `3024` | |
| **Commission on Civil Rights** | `3035` | |
| **Committee for Purchase From People Who Are Blind or Severely Disabled** | `3037` | |
| **Commodity Futures Trading Commission** | `3038` | |
| **Community Services Administration [INACTIVATED 1981]** | `3039` | |
| **Consumer Financial Protection Bureau** | `3170` | |
| **Consumer Product Safety Commission** | `3041` | |
| **Corporation for National and Community Service** | `3045` | |
| **Council on Environmental Quality** | `0331` | |
| **Court Services and Offender Supervision Agency for the District of Columbia** | `3225` | |
| **Department of Agriculture** | `0500` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Agricultural Cooperative Service | `0500` | `0537` |
| &nbsp;&nbsp;&nbsp;&nbsp;Agricultural Marketing Service | `0500` | `0581` |
| &nbsp;&nbsp;&nbsp;&nbsp;Agricultural Research Service | `0500` | `0518` |
| &nbsp;&nbsp;&nbsp;&nbsp;Animal and Plant Health Inspection Service | `0500` | `0579` |
| &nbsp;&nbsp;&nbsp;&nbsp;Client Technology Services | `0500` | `0517` |
| &nbsp;&nbsp;&nbsp;&nbsp;Commodity Credit Corporation | `0500` | `0566` |
| &nbsp;&nbsp;&nbsp;&nbsp;Economic Research Service | `0500` | `0536` |
| &nbsp;&nbsp;&nbsp;&nbsp;Extension Service | `0500` | `0527` |
| &nbsp;&nbsp;&nbsp;&nbsp;Farm Production and Conservation Business Center | `0500` | `0565` |
| &nbsp;&nbsp;&nbsp;&nbsp;Farm Service Agency | `0500` | `0560` |
| &nbsp;&nbsp;&nbsp;&nbsp;Federal Crop Insurance Corporation | `0500` | `0563` |
| &nbsp;&nbsp;&nbsp;&nbsp;Food and Nutrition Service | `0500` | `0584` |
| &nbsp;&nbsp;&nbsp;&nbsp;Food Safety and Inspection Service | `0500` | `0583` |
| &nbsp;&nbsp;&nbsp;&nbsp;Foreign Agricultural Service | `0500` | `0551` |
| &nbsp;&nbsp;&nbsp;&nbsp;Foreign Assistance Programs | `0500` | `0557` |
| &nbsp;&nbsp;&nbsp;&nbsp;Forest Service | `0500` | `0596` |
| &nbsp;&nbsp;&nbsp;&nbsp;Grain Inspection, Packers and Stockyards Administration | `0500` | `0580` |
| &nbsp;&nbsp;&nbsp;&nbsp;Human Nutrition Information Service | `0500` | `0586` |
| &nbsp;&nbsp;&nbsp;&nbsp;National Agricultural Library | `0500` | `0530` |
| &nbsp;&nbsp;&nbsp;&nbsp;National Agricultural Statistical Service | `0500` | `0535` |
| &nbsp;&nbsp;&nbsp;&nbsp;National Institute of Food and Agriculture | `0500` | `0524` |
| &nbsp;&nbsp;&nbsp;&nbsp;Natural Resources Conservation Service | `0500` | `0578` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Chief Financial Officer | `0500` | `0505` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Civil Rights | `0500` | `0508` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Communications | `0500` | `0506` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Contracting and Procurement | `0500` | `0599` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Energy | `0500` | `0598` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Grants and Program Systems | `0500` | `0525` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Homeland Security | `0500` | `0509` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Inspector General | `0500` | `0504` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of International Cooperation & Development | `0500` | `0577` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Rural Development Policy | `0500` | `0576` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the General Counsel | `0500` | `0510` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Secretary | `0500` | `0503` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Transportation | `0500` | `0507` |
| &nbsp;&nbsp;&nbsp;&nbsp;Packers and Stockyards Administration | `0500` | `0590` |
| &nbsp;&nbsp;&nbsp;&nbsp;Policy, E-Government and Fair Information Practices | `0500` | `0513` |
| &nbsp;&nbsp;&nbsp;&nbsp;Rural Business-Cooperative Service | `0500` | `0570` |
| &nbsp;&nbsp;&nbsp;&nbsp;Rural Housing Service | `0500` | `0575` |
| &nbsp;&nbsp;&nbsp;&nbsp;Rural Utilities Service | `0500` | `0572` |
| &nbsp;&nbsp;&nbsp;&nbsp;Science and Education | `0500` | `0531` |
| &nbsp;&nbsp;&nbsp;&nbsp;World Agricultural Outlook Board | `0500` | `0550` |
| **Department of Commerce** | `0600` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of Economic Analysis | `0600` | `0691` |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of Industry and Security | `0600` | `0694` |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of the Census | `0600` | `0607` |
| &nbsp;&nbsp;&nbsp;&nbsp;Economic and Statistical Analysis | `0600` | `0608` |
| &nbsp;&nbsp;&nbsp;&nbsp;Economic Development Administration | `0600` | `0610` |
| &nbsp;&nbsp;&nbsp;&nbsp;General Administration | `0600` | `0605` |
| &nbsp;&nbsp;&nbsp;&nbsp;International Trade Administration | `0600` | `0625` |
| &nbsp;&nbsp;&nbsp;&nbsp;Minority Business Development Agency | `0600` | `0640` |
| &nbsp;&nbsp;&nbsp;&nbsp;National Institute of Standards and Technology | `0600` | `0693` |
| &nbsp;&nbsp;&nbsp;&nbsp;National Oceanic and Atmospheric Administration | `0600` | `0648` |
| &nbsp;&nbsp;&nbsp;&nbsp;National Technical Information Service | `0600` | `0692` |
| &nbsp;&nbsp;&nbsp;&nbsp;National Telecommunications and Information Administration | `0600` | `0660` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Secretary | `0600` | `0690` |
| &nbsp;&nbsp;&nbsp;&nbsp;Patent and Trademark Office | `0600` | `0651` |
| &nbsp;&nbsp;&nbsp;&nbsp;Science and Technical Research | `0600` | `0652` |
| &nbsp;&nbsp;&nbsp;&nbsp;United States Travel and Tourism Administration | `0600` | `0644` |
| **Department of Education** | `1800` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Institute of Education Sciences | `1800` | `1850` |
| &nbsp;&nbsp;&nbsp;&nbsp;National Institute for Literacy | `1800` | `1893` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office for Civil Rights | `1800` | `1870` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Career, Technical, and Adult Education | `1800` | `1830` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Communications and Outreach | `1800` | `1860` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Elementary and Secondary Education | `1800` | `1810` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of English Language Acquistion | `1800` | `1885` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Federal Student Aid | `1800` | `1845` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Innovation and Improvement | `1800` | `1855` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Inspector General | `1800` | `1892` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Management | `1800` | `1880` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Planning, Evaluation and Policy Development | `1800` | `1875` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Postsecondary Education | `1800` | `1840` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Safe and Drug-Free Schools | `1800` | `1865` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Special Education and Rehabilitative Services | `1800` | `1820` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Chief Financial Officer | `1800` | `1890` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Chief Information Officer | `1800` | `1891` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the General Counsel | `1800` | `1801` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Secretary | `1800` | `1894` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Under Secretary | `1800` | `1895` |
| **Department of Energy** | `1900` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Defense and Security Affairs | `1900` | `1992` |
| &nbsp;&nbsp;&nbsp;&nbsp;Departmental and Others | `1900` | `1901` |
| &nbsp;&nbsp;&nbsp;&nbsp;Economic Regulatory Administration | `1900` | `1903` |
| &nbsp;&nbsp;&nbsp;&nbsp;Energy Efficiency and Renewable Energy | `1900` | `1904` |
| &nbsp;&nbsp;&nbsp;&nbsp;Energy Information Administration | `1900` | `1905` |
| &nbsp;&nbsp;&nbsp;&nbsp;National Nuclear Security Administration | `1900` | `1994` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Acquisition Management | `1900` | `1991` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Administration | `1900` | `1910` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of General Counsel | `1900` | `1990` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of State and Community Energy Programs | `1900` | `1930` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Chief Financial Officer | `1900` | `1920` |
| &nbsp;&nbsp;&nbsp;&nbsp;Policy, Safety, and Environment | `1900` | `1993` |
| **Department of Health and Human Services** | `0900` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Administration for Children and Families | `0900` | `0970` |
| &nbsp;&nbsp;&nbsp;&nbsp;Administration for Community Living | `0900` | `0985` |
| &nbsp;&nbsp;&nbsp;&nbsp;Administration for Strategic Preparedness and Response | `0900` | `0908` |
| &nbsp;&nbsp;&nbsp;&nbsp;Agency for Healthcare Research and Quality | `0900` | `0919` |
| &nbsp;&nbsp;&nbsp;&nbsp;Agency for Healthcare Research and Quality | `0900` | `0935` |
| &nbsp;&nbsp;&nbsp;&nbsp;Agency for Toxic Substances and Disease Registry | `0900` | `0923` |
| &nbsp;&nbsp;&nbsp;&nbsp;Centers for Disease Control and Prevention | `0900` | `0920` |
| &nbsp;&nbsp;&nbsp;&nbsp;Centers for Medicare & Medicaid Services | `0900` | `0938` |
| &nbsp;&nbsp;&nbsp;&nbsp;Departmental Management | `0900` | `0990` |
| &nbsp;&nbsp;&nbsp;&nbsp;Food and Drug Administration | `0900` | `0910` |
| &nbsp;&nbsp;&nbsp;&nbsp;Health Resources and Services Administration | `0900` | `0906` |
| &nbsp;&nbsp;&nbsp;&nbsp;Health Services Administration | `0900` | `0915` |
| &nbsp;&nbsp;&nbsp;&nbsp;Indian Health Service | `0900` | `0917` |
| &nbsp;&nbsp;&nbsp;&nbsp;National Institutes of Health | `0900` | `0925` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office for Civil Rights | `0900` | `0945` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Assistant Secretary for Health | `0900` | `0937` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Consumer Information and Insurance Oversight | `0900` | `0950` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Family Assistance | `0900` | `0992` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Human Development Services | `0900` | `0980` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Public Health and Science | `0900` | `0940` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Inspector General | `0900` | `0936` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the National Coordinator for Health Information Technology | `0900` | `0955` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Secretary | `0900` | `0991` |
| &nbsp;&nbsp;&nbsp;&nbsp;Program Support Center | `0900` | `0907` |
| &nbsp;&nbsp;&nbsp;&nbsp;Public Health Service | `0900` | `0905` |
| &nbsp;&nbsp;&nbsp;&nbsp;Substance Abuse and Mental Health Services Administration | `0900` | `0930` |
| **Department of Homeland Security** | `1600` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Customs Revenue Functions | `1600` | `1685` |
| &nbsp;&nbsp;&nbsp;&nbsp;Cybersecurity and Infrastructure Security Agency | `1600` | `1670` |
| &nbsp;&nbsp;&nbsp;&nbsp;Directorate of Border and Transportation Security | `1600` | `1650` |
| &nbsp;&nbsp;&nbsp;&nbsp;Directorate of Information and Analysis and Infrastructure Protection | `1600` | `1630` |
| &nbsp;&nbsp;&nbsp;&nbsp;Directorate of Science and Technology | `1600` | `1640` |
| &nbsp;&nbsp;&nbsp;&nbsp;Federal Emergency Management Agency | `1600` | `1660` |
| &nbsp;&nbsp;&nbsp;&nbsp;Homeland Security Advanced Research Projects Agency | `1600` | `1641` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Civil Rights | `1600` | `1610` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Inspector General | `1600` | `1690` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Secretary | `1600` | `1601` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Undersecretary for Management | `1600` | `1680` |
| &nbsp;&nbsp;&nbsp;&nbsp;Transportation Security Administration | `1600` | `1652` |
| &nbsp;&nbsp;&nbsp;&nbsp;U.S. Citizenship and Immigration Services | `1600` | `1615` |
| &nbsp;&nbsp;&nbsp;&nbsp;U.S. Coast Guard | `1600` | `1625` |
| &nbsp;&nbsp;&nbsp;&nbsp;U.S. Customs and Border Protection | `1600` | `1651` |
| &nbsp;&nbsp;&nbsp;&nbsp;U.S. Immigration and Customs Enforcement | `1600` | `1653` |
| &nbsp;&nbsp;&nbsp;&nbsp;U.S. Secret Service | `1600` | `1620` |
| **Department of Housing and Urban Development** | `2500` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Enforcement Center | `2500` | `2509` |
| &nbsp;&nbsp;&nbsp;&nbsp;Government National Mortgage Association | `2500` | `2503` |
| &nbsp;&nbsp;&nbsp;&nbsp;New Communities Development Corporation | `2500` | `2512` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Administration | `2500` | `2535` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Chief Information Officer | `2500` | `2513` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Community Planning and Development | `2500` | `2506` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Fair Housing and Equal Opportunity | `2500` | `2529` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Housing | `2500` | `2502` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Lead-Based Paint and Poison Prevention | `2500` | `2539` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Multifamily Assistance Restructuring | `2500` | `2505` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Public and Indian Housing | `2500` | `2577` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Chief Financial Officer | `2500` | `2511` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the General Counsel | `2500` | `2510` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Inspector General | `2500` | `2508` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Secretary | `2500` | `2501` |
| &nbsp;&nbsp;&nbsp;&nbsp;Policy Development and Research | `2500` | `2528` |
| &nbsp;&nbsp;&nbsp;&nbsp;Real Estate Assessment Center | `2500` | `2507` |
| &nbsp;&nbsp;&nbsp;&nbsp;Solar Energy and Energy Conservation Bank | `2500` | `2504` |
| **Department of Justice** | `1100` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of Alcohol, Tobacco, Firearms, and Explosives | `1100` | `1140` |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of Prisons | `1100` | `1120` |
| &nbsp;&nbsp;&nbsp;&nbsp;Civil Rights Division | `1100` | `1190` |
| &nbsp;&nbsp;&nbsp;&nbsp;Criminal Division | `1100` | `1123` |
| &nbsp;&nbsp;&nbsp;&nbsp;Drug Enforcement Administration | `1100` | `1117` |
| &nbsp;&nbsp;&nbsp;&nbsp;Executive Office for Immigration Review | `1100` | `1125` |
| &nbsp;&nbsp;&nbsp;&nbsp;Federal Bureau of Investigation | `1100` | `1110` |
| &nbsp;&nbsp;&nbsp;&nbsp;General Administration | `1100` | `1103` |
| &nbsp;&nbsp;&nbsp;&nbsp;Immigration and Naturalization Service | `1100` | `1115` |
| &nbsp;&nbsp;&nbsp;&nbsp;Legal Activities | `1100` | `1105` |
| &nbsp;&nbsp;&nbsp;&nbsp;National Security Division | `1100` | `1124` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of  Violence Against Women | `1100` | `1122` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Justice Programs | `1100` | `1121` |
| &nbsp;&nbsp;&nbsp;&nbsp;United States Parole Commission | `1100` | `1104` |
| **Department of Labor** | `1200` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of Labor Statistics | `1200` | `1220` |
| &nbsp;&nbsp;&nbsp;&nbsp;Departmental Management | `1200` | `1225` |
| &nbsp;&nbsp;&nbsp;&nbsp;Employee Benefits Security Administration | `1200` | `1210` |
| &nbsp;&nbsp;&nbsp;&nbsp;Employment and Training Administration | `1200` | `1205` |
| &nbsp;&nbsp;&nbsp;&nbsp;Employment Standards Administration | `1200` | `1215` |
| &nbsp;&nbsp;&nbsp;&nbsp;Mine Safety and Health Administration | `1200` | `1219` |
| &nbsp;&nbsp;&nbsp;&nbsp;Occupational Safety and Health Administration | `1200` | `1218` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Disability Employment Policy | `1200` | `1230` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Federal Contract Compliance Programs | `1200` | `1250` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Labor-Management Standards | `1200` | `1245` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the American Workplace | `1200` | `1294` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the American Workplace/Office of Labor Management Standards | `1200` | `1214` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Assistant Secretary for Administration and Management | `1200` | `1291` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Assistant Secretary for Veterans' Employment and Training | `1200` | `1293` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Inspector General | `1200` | `1292` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Secretary | `1200` | `1290` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Workers' Compensation Programs | `1200` | `1240` |
| &nbsp;&nbsp;&nbsp;&nbsp;Wage and Hour Division | `1200` | `1235` |
| **Department of State** | `1400` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Administration of Foreign Affairs | `1400` | `1405` |
| **Department of the Interior** | `1000` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Assistant Secretary for Land and Minerals Management | `1000` | `1082` |
| &nbsp;&nbsp;&nbsp;&nbsp;Assistant Secretary for Policy, Management and Budget | `1000` | `1090` |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of Indian Affairs | `1000` | `1076` |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of Land Management | `1000` | `1004` |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of Mines | `1000` | `1032` |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of Ocean Energy Management | `1000` | `1010` |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of Reclamation | `1000` | `1006` |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of Safety and Environmental Enforcement | `1000` | `1014` |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of Trust Funds Administration | `1000` | `1035` |
| &nbsp;&nbsp;&nbsp;&nbsp;Geological Survey | `1000` | `1028` |
| &nbsp;&nbsp;&nbsp;&nbsp;Indian Arts and Crafts Board | `1000` | `1085` |
| &nbsp;&nbsp;&nbsp;&nbsp;National Biological Service | `1000` | `1089` |
| &nbsp;&nbsp;&nbsp;&nbsp;National Park Service | `1000` | `1024` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office for Equal Opportunity | `1000` | `1091` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Acquisition and Property Management | `1000` | `1084` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Hearings and Appeals | `1000` | `1094` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Natural Resources Revenue | `1000` | `1012` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Planning and Performance Management | `1000` | `1040` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Surface Mining Reclamation and Enforcement | `1000` | `1029` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Inspector General | `1000` | `1095` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Secretary | `1000` | `1093` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Solicitor | `1000` | `1092` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Water Policy | `1000` | `1008` |
| &nbsp;&nbsp;&nbsp;&nbsp;United States Fish and Wildlife Service | `1000` | `1018` |
| **Department of the Treasury** | `1500` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Alcohol and Tobacco Tax and Trade Bureau | `1500` | `1513` |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of Alcohol, Tobacco and Firearms | `1500` | `1512` |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of Engraving and Printing | `1500` | `1520` |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of the Fiscal Service | `1500` | `1530` |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of the Public Debt | `1500` | `1535` |
| &nbsp;&nbsp;&nbsp;&nbsp;Community Development Financial Institutions Fund | `1500` | `1559` |
| &nbsp;&nbsp;&nbsp;&nbsp;Comptroller of the Currency | `1500` | `1557` |
| &nbsp;&nbsp;&nbsp;&nbsp;Customs Revenue Function | `1500` | `1515` |
| &nbsp;&nbsp;&nbsp;&nbsp;Departmental Offices | `1500` | `1505` |
| &nbsp;&nbsp;&nbsp;&nbsp;Financial Crimes Enforcement Network | `1500` | `1506` |
| &nbsp;&nbsp;&nbsp;&nbsp;Financial Management Service | `1500` | `1510` |
| &nbsp;&nbsp;&nbsp;&nbsp;Internal Revenue Service | `1500` | `1545` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Revenue Sharing | `1500` | `1507` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the General Counsel | `1500` | `1590` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Thrift Supervision | `1500` | `1550` |
| &nbsp;&nbsp;&nbsp;&nbsp;Thrift Depositor Protection Oversight Board [TRANSFERRED TO 1505 in 1996] | `1500` | `1551` |
| &nbsp;&nbsp;&nbsp;&nbsp;Treasury Inspector General for Tax Administration | `1500` | `1591` |
| &nbsp;&nbsp;&nbsp;&nbsp;United States Mint | `1500` | `1525` |
| &nbsp;&nbsp;&nbsp;&nbsp;United States Secret Service | `1500` | `1555` |
| **Department of Transportation** | `2100` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Bureau of Transportation Statistics - Aviation | `2100` | `2138` |
| &nbsp;&nbsp;&nbsp;&nbsp;Federal Aviation Administration | `2100` | `2120` |
| &nbsp;&nbsp;&nbsp;&nbsp;Federal Highway Administration | `2100` | `2125` |
| &nbsp;&nbsp;&nbsp;&nbsp;Federal Motor Carrier Safety Administration | `2100` | `2126` |
| &nbsp;&nbsp;&nbsp;&nbsp;Federal Railroad Administration | `2100` | `2130` |
| &nbsp;&nbsp;&nbsp;&nbsp;Federal Transit Administration | `2100` | `2132` |
| &nbsp;&nbsp;&nbsp;&nbsp;Maritime Administration | `2100` | `2133` |
| &nbsp;&nbsp;&nbsp;&nbsp;National Highway Traffic Safety Administration | `2100` | `2127` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Secretary | `2100` | `2105` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Secretary - Aviation | `2100` | `2106` |
| &nbsp;&nbsp;&nbsp;&nbsp;Pipeline and Hazardous Materials Safety Administration | `2100` | `2137` |
| &nbsp;&nbsp;&nbsp;&nbsp;Pipeline and Hazardous Materials Safety Administration | `2100` | `2145` |
| &nbsp;&nbsp;&nbsp;&nbsp;Research and Innovative Technologies Administration | `2100` | `2139` |
| &nbsp;&nbsp;&nbsp;&nbsp;Research and Innovative Technologies Administration (Old) | `2100` | `2150` |
| &nbsp;&nbsp;&nbsp;&nbsp;Saint Lawrence Seaway Development Corporation | `2100` | `2135` |
| &nbsp;&nbsp;&nbsp;&nbsp;Transportation Security Administration | `2100` | `2110` |
| &nbsp;&nbsp;&nbsp;&nbsp;U.S. Coast Guard | `2100` | `2115` |
| **Department of Veterans Affairs** | `2900` | |
| **Department of War** | `0700` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Defense Acquisition Regulations Council | `0700` | `0750` |
| &nbsp;&nbsp;&nbsp;&nbsp;Defense Finance and Accounting Service | `0700` | `0730` |
| &nbsp;&nbsp;&nbsp;&nbsp;Department of the Air Force | `0700` | `0701` |
| &nbsp;&nbsp;&nbsp;&nbsp;Department of the Army | `0700` | `0702` |
| &nbsp;&nbsp;&nbsp;&nbsp;Department of the Navy | `0700` | `0703` |
| &nbsp;&nbsp;&nbsp;&nbsp;Departmental and Others | `0700` | `0704` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Assistant Secretary for Health Affairs | `0700` | `0720` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Secretary | `0700` | `0790` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Under Secretary of Defense for Intelligence | `0700` | `0705` |
| &nbsp;&nbsp;&nbsp;&nbsp;Space Force | `0700` | `0715` |
| &nbsp;&nbsp;&nbsp;&nbsp;U.S. Army Corps of Engineers | `0700` | `0710` |
| &nbsp;&nbsp;&nbsp;&nbsp;US Marine Corps | `0700` | `0712` |
| **DOD/GSA/NASA (FAR)** | `9000` | |
| **Emergency Oil and Gas Guaranteed Loan Board** | `3003` | |
| **Emergency Steel Guarantee Loan Board** | `3004` | |
| **Environmental Protection Agency** | `2000` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Air and Radiation | `2000` | `2060` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Chemical Safety and Pollution Prevention | `2000` | `2070` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Enforcement and Compliance Assurance | `2000` | `2020` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Environmental Information | `2000` | `2025` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Environmental Justice and External Civil Rights | `2000` | `2035` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of General Counsel | `2000` | `2015` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Inspector General | `2000` | `2065` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of International and Tribal Affairs | `2000` | `2045` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Land and Emergency Management | `2000` | `2050` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Mission Support | `2000` | `2030` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Policy | `2000` | `2010` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Research and Development | `2000` | `2080` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Administrator | `2000` | `2090` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of the Chief Financial Officer | `2000` | `2055` |
| &nbsp;&nbsp;&nbsp;&nbsp;Office of Water | `2000` | `2040` |
| &nbsp;&nbsp;&nbsp;&nbsp;Regional Office Atlanta | `2000` | `2004` |
| &nbsp;&nbsp;&nbsp;&nbsp;Regional Office Boston | `2000` | `2001` |
| &nbsp;&nbsp;&nbsp;&nbsp;Regional Office Chicago | `2000` | `2005` |
| &nbsp;&nbsp;&nbsp;&nbsp;Regional Office Dallas | `2000` | `2006` |
| &nbsp;&nbsp;&nbsp;&nbsp;Regional Office Denver | `2000` | `2008` |
| &nbsp;&nbsp;&nbsp;&nbsp;Regional Office Kansas City | `2000` | `2007` |
| &nbsp;&nbsp;&nbsp;&nbsp;Regional Office New York | `2000` | `2002` |
| &nbsp;&nbsp;&nbsp;&nbsp;Regional Office Philadelphia | `2000` | `2003` |
| &nbsp;&nbsp;&nbsp;&nbsp;Regional Office San Francisco | `2000` | `2009` |
| &nbsp;&nbsp;&nbsp;&nbsp;Regional Office Seattle | `2000` | `2012` |
| **Equal Employment Opportunity Commission** | `3046` | |
| **Executive Office of the President** | `0300` | |
| **Export-Import Bank of the United States** | `3048` | |
| **Farm Credit System Assistance Board** | `3053` | |
| **Federal Communications Commission** | `3060` | |
| **Federal Deposit Insurance Corporation** | `3064` | |
| **Federal Emergency Management Agency** | `3067` | |
| **Federal Energy Regulatory Commission** | `1902` | |
| **Federal Home Loan Bank Board** | `3068` | |
| **Federal Housing Finance Agency** | `2590` | |
| **Federal Maritime Commission** | `3072` | |
| **Federal Mediation and Conciliation Service** | `3076` | |
| **Federal Permitting Improvement Steering Council** | `3121` | |
| **Federal Trade Commission** | `3084` | |
| **Financial Stability Oversight Council** | `4030` | |
| **General Services Administration** | `3090` | |
| **Institute of Museum and Library Services** | `3137` | |
| **Inter-American Foundation** | `0417` | |
| **Interstate Commerce Commission** | `3120` | |
| **James Madison Memorial Fellowship Foundation** | `3020` | |
| **Merit Systems Protection Board** | `3124` | |
| **National Aeronautics and Space Administration** | `2700` | |
| &nbsp;&nbsp;&nbsp;&nbsp;Kennedy Space Center | `2700` | `2730` |
| **National Archives and Records Administration** | `3095` | |
| **National Capital Planning Commission** | `3125` | |
| **National Credit Union Administration** | `3133` | |
| **National Endowment for the Arts** | `3135` | |
| **National Endowment for the Humanities** | `3136` | |
| **National Indian Gaming Commission** | `3141` | |
| **National Science Foundation** | `3145` | |
| **Nuclear Regulatory Commission** | `3150` | |
| **Office of Director of National Intelligence** | `3440` | |
| **Office of Federal Housing Enterprise Oversight** | `2550` | |
| **Office of Government Ethics** | `3209` | |
| **Office of Management and Budget** | `0348` | |
| **Office of National Drug Control Policy** | `3201` | |
| **Office of Navajo and Hopi Indian Relocation** | `3148` | |
| **Office of Personnel Management** | `3206` | |
| **Office of Science and Technology Policy** | `0349` | |
| **Office of Special Counsel** | `3255` | |
| **Office of the Federal Inspector, Alaska Natural Gas Transportation System** | `3204` | |
| **Office of the United States Trade Representative** | `0350` | |
| **Other Independent Agencies** | `3200` | |
| **Other Temporary Commissions** | `3312` | |
| **Overseas Private Investment Corporation** | `3420` | |
| **Panama Canal Commission** | `3207` | |
| **Peace Corps** | `0420` | |
| **Pennsylvania Avenue Development Corporation** | `3208` | |
| **Pension Benefit Guaranty Corporation** | `1212` | |
| **Railroad Retirement Board** | `3220` | |
| **Resolution Trust Corporation** | `3205` | |
| **Securities and Exchange Commission** | `3235` | |
| **Selective Service System** | `3240` | |
| **Small Business Administration** | `3245` | |
| **Social Security Administration** | `0960` | |
| **Surface Transportation Board** | `2140` | |
| **Tennessee Valley Authority** | `3316` | |
| **Thrift Depositor Protection Oversight Board** | `3203` | |
| **U.S. Commission on Civil Rights** | `3035` | |
| **United States Information Agency** | `3116` | |
| **United States Metric Board** | `3327` | |
| **United States Postal Service** | `3210` | |
| &nbsp;&nbsp;&nbsp;&nbsp;United States Postal Inspection Service | `3210` | `3213` |
| **Water Resources Council [INACTIVATED 1982]** | `3335` | |

## 3. Record Identifiers Used by `reginfo-reg-download.py`

Beyond the form's search parameters, two identifiers show up embedded in result-row links and
are how `reginfo-reg-download.py` locates a RIN's full record:

| Identifier | Found In | Used For |
| :--- | :--- | :--- |
| `pubId` | The RIN's link to `eAgendaViewRule?pubId=...&RIN=...` | Identifies a Unified Agenda publication cycle (e.g. `202410` = Fall 2024). Each cycle a RIN is carried in gets its own View Rule snapshot. |
| `rrid` | The Status column's link to `eoDetails?rrid=...` (only present once a submission has concluded) | Identifies one concluded EO 12866 review record for the RIN. |
