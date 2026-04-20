"""Sample FPL bill text used as a parser test fixture.

Taken from FPL's public "How to read your bill" PDF
(``fpl.com/content/dam/fplgp/us/en/northwest/pdf/rates/how-to-read-your-bill.pdf``),
which embeds a fully-redacted sample bill as a reference for customers.
Extracted verbatim via ``pdfplumber`` with whitespace artifacts preserved
— this is what a real FPL bill looks like after PDF-to-text extraction,
warts and all, and is the correct stress test for the parser.

The sample bill's numbers correspond to a **NW Florida 2025 Feb residential
customer** (rate RS-1, 1,079 kWh consumed, June 2 – July 1, 2025 service,
base $9.61, total $180.34).
"""

FPL_SAMPLE_BILL_TEXT = """\
How to read your bill

FPL.com

Service period: June 3, 2025 to July 1, 2025 (29 days)
Statement Date: July 2, 2025
Account Number: 2112133485-56178 82940
Service Address: 11203 MAIN STREET, PENSACOLA, FL 32503

Hello Timothy Winkler,
Here's what you owe for this billing period.

CURRENT BILL: $180.34
TOTAL AMOUNT YOU OWE: $180.34

NEW CHARGES DUE BY Jul 22, 2025

BILL SUMMARY
Amount of your last bill 206.11
Payment(s) received - thank you -206.11
Balance before new charges 0.00
Total new charges 180.34
Total amount due 180.34

Payments received after July 22, 2025 are considered late; a late payment
charge, the greater of $5.00 or 1.50 % of your past due balance will apply.

Report Power Outages: 800-468-8243
Customer Service: 800-225-5797

BILL DETAILS
New Charges
Rate: RS-1 RESIDENTIAL SERVICE
Base charge 9.61
Non-fuel 115.39
Fuel charge 26.77
Electric service charges 151.77
Gross receipts tax (State tax) 3.89
Franchise fee (Reqd local fee) 9.90
Utility tax (Local tax) 14.64
Regulatory fee (State fee) 0.1416
Taxes and charges 28.57
Total new charges 180.34
Total amount you owe 180.34

METER SUMMARY
Meter Reading - Meter 5854432. Next meter reading date Aug 1, 2025
Usage Type Current - Previous = Usage
kWh 69792 - 68713 = 1079

ENERGY USE COMPARISON
This Month Last Month Last Year
Service to Jul 1, 2025 Jun 2, 2025 Jul 2, 2024
kWh used 1079 1224 1117
Service days 29 32 29
kWh/day 37 38 39
Amount $180.34 $206.11 $176.08
"""
