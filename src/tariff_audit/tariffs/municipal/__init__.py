"""Municipal and cooperative electric utilities — NOT PSC-regulated.

Florida has numerous municipal (city-owned) electric utilities and rural
electric cooperatives that are **outside the Florida Public Service
Commission's rate-regulation authority** for retail rates. Their rates are
set by their governing boards, not by PSC tariff, so a "forensic tariff
audit" in the sense this tool performs does not apply to them.

Major municipal/cooperative Florida electric utilities (non-exhaustive):

- **JEA** (Jacksonville)
- **OUC** (Orlando Utilities Commission)
- **City of Tallahassee Utilities**
- **Gainesville Regional Utilities (GRU)**
- **Lakeland Electric**
- **Kissimmee Utility Authority (KUA)**
- **City of Homestead**
- **Beaches Energy Services**
- **Seminole Electric Cooperative** (wholesale generation cooperative)
- **Clay Electric Cooperative**
- **Sumter Electric Cooperative (SECO)**
- **Withlacoochee River Electric Cooperative**
- **Choctawhatchee Electric Cooperative**
- **Central Florida Electric Cooperative**
- **Suwannee Valley Electric Cooperative**
- **Tri-County Electric Cooperative**
- **Peace River Electric Cooperative**
- **Glades Electric Cooperative**
- **Talquin Electric Cooperative**

What this tool CAN still do for municipal/cooperative customers:

1. Flat-rate verification against the utility's published rate book.
2. Multi-month trend anomaly detection (`engine.anomalies.SEASONAL`).
3. Meter-reading sanity checks.
4. Tax and franchise fee isolation.

What this tool explicitly CANNOT do for them (without PSC-regulated tariff):

1. DETERMINISTIC-tier bill reconstruction (we have no PSC-approved tariff
   to reconstruct against).
2. PSC complaint generation (PSC has no jurisdiction).

A future module may add "municipal rate book" support for any municipal
utility whose rate structure is published in machine-readable form.
"""

# Intentionally empty — no tariff schedules registered.
