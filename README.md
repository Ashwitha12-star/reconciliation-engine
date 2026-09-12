
# Cross-System Reconciliation & Tenant Isolation

A full-stack reconciliation tool built for the AdosX Engineering Full-Stack Engineer take-home assignment.

The application imports System A and System B CSV exports, maps records to organizations through `locations.csv`, detects discrepancies, and displays them in a tenant-scoped React dashboard.

## Tech Stack

- Backend: Python, Django
- Database: SQLite
- Frontend: React, Vite
- Testing: Django `unittest` / `SimpleTestCase`
- Data format: CSV

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
- Normalizes System B references for matching.
- Stores original reference values for auditability.
- Maps every location to its organization.
- Does not silently reject malformed data rows.

With the supplied AdosX data, the importer successfully loads:

- 120 System A rows
- 121 System B rows

### 2. Reconciliation Engine

The comparison logic is kept separate from the HTTP/API layer.

Records are matched using:

```text
(organization, normalized_record_id)

This prevents records belonging to different tenants from being matched together.

The reconciliation engine detects:

MISSING_IN_SYSTEM_B
ORPHAN_IN_SYSTEM_B
DUPLICATE_IN_SYSTEM_B
VALUE_MISMATCH

System A total_value is compared with System B value.

Numeric values are normalized using Decimal, allowing values such as:

1,25,400.00

to be compared safely with numeric representations.

Event dates are also compared:

System A: event_date
System B: recorded_on

A difference is reported as VALUE_MISMATCH.

3. Tenant Isolation

The API requires an organization ID.

Before reconciliation, System A and System B records are filtered by the selected organization through their location relationship.

This means an organization can only receive discrepancy results belonging to its own locations.

The organization is therefore part of the reconciliation matching key rather than being applied only as a frontend filter.

4. React Dashboard

The frontend provides:

Organization selector
Discrepancy reason filter
Ascending/descending value sorting
Discrepancy count
Record/reference
Location
Organization
System A value
System B value

The UI intentionally remains simple because the assignment prioritizes correctness and functionality over visual design.

Project Structure
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
Setup
Requirements
Python 3.10+
Node.js 18+ or 20+ LTS
npm
1. Clone the Repository
git clone <YOUR_PRIVATE_REPOSITORY_URL>
cd reconciliation-engine
2. Create and Activate the Python Virtual Environment
Windows
python -m venv venv
venv\Scripts\activate
macOS/Linux
python3 -m venv venv
source venv/bin/activate
3. Install Backend Dependencies
cd backend
python -m pip install -r requirements.txt
4. Create the Database
python manage.py migrate
5. Import the CSV Data
python manage.py import_data

Expected output for the supplied dataset:

Imported 120 System A rows and 121 System B rows. No malformed rows were rejected.
6. Run the Backend
python manage.py runserver

The Django API will run at:

http://127.0.0.1:8000/
7. Install Frontend Dependencies

Open a second terminal from the project root:

cd frontend
npm install
8. Run the Frontend
npm run dev

Open the Vite URL shown in the terminal, normally:

http://localhost:5173/
Running Tests

From the backend directory:

python manage.py test

The comparison test suite covers:

Missing System B records
Orphan System B records
Duplicate System B entries
Value mismatches
Numeric formatting
Tenant boundary isolation

The current test suite contains 6 tests and passes successfully.

What I Deliberately Did Not Build

The assignment is intentionally scoped to a small dataset, so I did not build:

Authentication or user accounts
Authorization roles
Pagination
Background processing
Multi-database tenant routing
PostgreSQL infrastructure
Complex UI styling
Export functionality
Large-scale performance optimizations

These were intentionally left out to keep the submission focused on reconciliation correctness, dirty-data handling, tenant isolation, tests, and clarity.

How I Worked With the AI Agent

I used an AI coding agent as an implementation and review assistant.

I used it to help with:

Initial project structure
Django model and importer scaffolding
Reconciliation logic
React components
Test cases
Debugging implementation issues
Reviewing tenant isolation
Reviewing the final implementation against the assignment requirements

I did not treat generated code as automatically correct. I ran the application, inspected the actual results against the supplied CSV data, and corrected implementation and test issues when they appeared.

I also manually verified the dashboard using the supplied AdosX data and checked each required discrepancy category.

AI Agent Blindspot

One issue the AI agent got wrong was the initial assumption that the System A model used a generic raw_value field. The supplied System A CSV actually contains a total_value field, while System B contains value.

I noticed the problem when the updated reconciliation code caused the existing numeric-formatting test to fail.

I then changed the model, importer, comparator, API view, and tests to use the actual CSV fields.

I also verified the result against the real 120-row System A dataset and 121-row System B dataset rather than relying only on sample data.

Least Confident Area

The part I am least confident about is reference normalization.

The implementation removes non-alphanumeric characters and lowercases references before matching. This handles variations such as spaces, underscores, and dashes while preserving the original values.

However, real production exports could contain more complicated reference transformations that cannot safely be inferred from this dataset. A larger set of documented normalization rules or an explicit source-system contract would make this more robust.

If I Had a Second Day

My first priority would be to strengthen the reconciliation and ingestion boundary with additional integration tests.

In particular, I would add API-level tenant-isolation tests and more dirty-data cases for malformed references, blank fields, unusual numeric formats, and duplicate records.

I would also improve error reporting around CSV ingestion so that problematic rows could be audited explicitly while still remaining in the database.

Verification

The supplied AdosX dataset was successfully imported without rejected rows:

System A: 120 rows
System B: 121 rows

The backend test suite passes:

Found 6 test(s).
......
Ran 6 tests
OK

The dashboard was also manually verified for:

Missing in System B
Orphan in System B
Duplicate in System B
Value mismatch
Organization filtering
Value sorting
Tenant isolation
License

This project was created as a take-home engineering assessment for AdosX Engineering.
