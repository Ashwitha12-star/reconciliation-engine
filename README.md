# Cross-System Reconciliation & Tenant Isolation

A full-stack reconciliation tool built for the **AdosX Engineering Full-Stack Engineer take-home assignment**.

The application imports System A and System B CSV exports, maps records to organizations through `locations.csv`, detects discrepancies, and displays them in a tenant-scoped React dashboard.

---

## Tech Stack

- **Backend:** Python, Django
- **Database:** SQLite
- **Frontend:** React, Vite
- **Testing:** Django `unittest` / `SimpleTestCase`
- **Data Format:** CSV

---

## What I Built

### 1. Resilient CSV Ingestion

The importer loads:

- `data/system_a.csv`
- `data/system_b.csv`
- `data/locations.csv`

The importer:

- Reads CSV values defensively.
- Preserves source values as strings.
- Handles blank and non-standard values without crashing.
- Normalizes System A and System B references for matching.
- Stores original reference values for auditability.
- Maps locations to their organizations using `locations.csv`.
- Does not silently reject malformed data rows.

With the supplied AdosX dataset, the importer successfully loads:

- **120 System A rows**
- **121 System B rows**

Expected output:

```text
Imported 120 System A rows and 121 System B rows. No malformed rows were rejected.
```

---

### 2. Reconciliation Engine

The comparison logic is kept separate from the HTTP/API layer.

Records are matched using:

```text
(organization, normalized_record_id)
```

This prevents records belonging to different tenants from being matched accidentally.

The reconciliation engine detects the following discrepancy types:

```text
MISSING_IN_SYSTEM_B
ORPHAN_IN_SYSTEM_B
DUPLICATE_IN_SYSTEM_B
VALUE_MISMATCH
```

#### Value Comparison

System A `total_value` is compared with System B `value`.

Numeric values are parsed using Python's `Decimal` type so that different numeric representations can be compared safely.

For example:

```text
System A: 125400.00
System B: 1,25,400.00
```

These values are treated as numerically equal.

#### Date Comparison

System A `event_date` is compared with System B `recorded_on`.

If the dates differ, the reconciliation engine reports a:

```text
VALUE_MISMATCH
```

The original values are preserved in the discrepancy response so that the difference can be inspected.

---

### 3. Tenant Isolation

The API requires an organization ID.

Before reconciliation, System A and System B records are filtered by the selected organization through their location relationship.

The organization is also part of the reconciliation matching key:

```text
(organization, normalized_record_id)
```

This means a record from one organization cannot accidentally match a record with the same reference belonging to another organization.

Tenant isolation is therefore enforced in the backend rather than relying only on frontend filtering.

---

### 4. React Dashboard

The frontend provides:

- Organization selector
- Discrepancy reason filter
- Ascending/descending value sorting
- Discrepancy count
- Record/reference
- Location
- Organization
- System A value
- System B value

The UI intentionally remains simple because the assignment prioritizes correctness, reconciliation logic, tenant isolation, dirty-data handling, and testing over visual design.

---

## Project Structure

```text
reconciliation-engine/
├── backend/
│   ├── core/
│   ├── reconciler/
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── import_data.py
│   │   ├── migrations/
│   │   ├── services/
│   │   │   └── comparator.py
│   │   ├── tests/
│   │   │   └── test_comparator.py
│   │   ├── models.py
│   │   └── views.py
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DiscrepancyTable.jsx
│   │   │   └── FilterBar.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── data/
│   ├── system_a.csv
│   ├── system_b.csv
│   └── locations.csv
├── DECISIONS.md
└── README.md
```

---

## Setup

### Requirements

- Python 3.10+
- Node.js 18+ or Node.js 20+ LTS
- npm
- Git

---

### 1. Clone the Repository

Replace the placeholder with the private GitHub repository URL.

```bash
git clone <YOUR_PRIVATE_REPOSITORY_URL>
cd reconciliation-engine
```

---

### 2. Create and Activate the Python Virtual Environment

#### Windows

```bat
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Backend Dependencies

From the project root:

```bash
cd backend
python -m pip install -r requirements.txt
```

---

### 4. Create the Database

Run:

```bash
python manage.py migrate
```

---

### 5. Import the CSV Data

Run:

```bash
python manage.py import_data
```

Expected output:

```text
Imported 120 System A rows and 121 System B rows. No malformed rows were rejected.
```

---

### 6. Run the Backend

Run:

```bash
python manage.py runserver
```

The Django API will run at:

```text
http://127.0.0.1:8000/
```

Keep this terminal running.

---

### 7. Install Frontend Dependencies

Open a second terminal from the project root.

```bash
cd frontend
npm install
```

---

### 8. Run the Frontend

Run:

```bash
npm run dev
```

Open the Vite URL shown in the terminal, normally:

```text
http://localhost:5173/
```

---

## Running Tests

From the `backend` directory, run:

```bash
python manage.py test
```

The comparison test suite covers:

- Missing System B records
- Orphan System B records
- Duplicate System B entries
- Value mismatches
- Numeric formatting
- Tenant boundary isolation
- Date mismatches

The current test suite contains **7 tests** and passes successfully.

Expected output:

```text
Found 7 test(s).
System check identified no issues (0 silenced).
.......
----------------------------------------------------------------------
Ran 7 tests in 0.029s

OK
```

---

## What I Deliberately Did Not Build

The assignment is intentionally scoped to a small dataset, so I did not build:

- Authentication or user accounts
- Authorization roles
- Pagination
- Background processing
- Multi-database tenant routing
- PostgreSQL infrastructure
- Complex UI styling
- Export functionality
- Large-scale performance optimizations

These were intentionally left out to keep the submission focused on:

- Reconciliation correctness
- Dirty-data handling
- Tenant isolation
- Automated tests
- Clear engineering decisions

---

## How I Worked With the AI Agent

I used an AI coding agent as an implementation and review assistant.

I used it to help with:

- Initial project structure
- Django model and importer scaffolding
- Reconciliation logic
- React components
- Test cases
- Debugging implementation issues
- Reviewing tenant isolation
- Reviewing the final implementation against the assignment requirements

I did not treat generated code as automatically correct.

I ran the application, inspected the actual results against the supplied CSV data, and corrected implementation and test issues when they appeared.

I also manually verified the dashboard using the supplied AdosX data and checked the required discrepancy categories.

---

## AI Agent Blindspot

One issue the AI agent got wrong was the initial assumption that the System A model used a generic `raw_value` field.

The supplied System A CSV actually contains:

```text
total_value
```

while System B contains:

```text
value
```

I noticed the problem when the updated reconciliation code caused the existing numeric-formatting test to fail.

I then changed the model, importer, comparator, API view, and tests to use the actual CSV fields.

I also verified the implementation against the real supplied dataset rather than relying only on sample data.

---

## Least Confident Area

The part I am least confident about is reference normalization.

The implementation removes non-alphanumeric characters and lowercases references before matching.

For example, formatting differences such as spaces, underscores, and dashes can be normalized before comparison while the original source value is preserved for auditability.

However, real production exports could contain more complicated reference transformations that cannot safely be inferred from this dataset.

A larger set of documented normalization rules or an explicit source-system contract would make this more robust.

---

## If I Had a Second Day

My first priority would be to strengthen the reconciliation and ingestion boundary with additional integration tests.

In particular, I would add:

- API-level tenant-isolation tests
- More malformed-reference test cases
- Blank-field test cases
- Additional unusual numeric-format cases
- More duplicate-record scenarios
- Explicit ingestion error reporting

I would also improve CSV ingestion reporting so that problematic rows could be audited explicitly while still remaining in the database.

---

## Verification

The supplied AdosX dataset was successfully imported without rejected rows:

```text
System A: 120 rows
System B: 121 rows
```

The backend test suite passes:

```text
Found 7 test(s).
System check identified no issues (0 silenced).
.......
----------------------------------------------------------------------
Ran 7 tests in 0.029s

OK
```

The dashboard was also manually verified for:

- Missing in System B
- Orphan in System B
- Duplicate in System B
- Value mismatch
- Date mismatch
- Organization filtering
- Value sorting
- Tenant isolation

---

## License

This project was created as a take-home engineering assessment for **AdosX Engineering**.
