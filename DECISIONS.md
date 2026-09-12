# Technical Decisions

## 1. Match records using organization + normalized reference

**Decision:**  
Match System A and System B records using `(org_id, normalized_record_id)`.

**Alternative rejected:**  
Match records using only the normalized record ID.

**Reasoning:**  
The same record reference can appear in different tenants. Including the organization in the matching key prevents cross-tenant matches and protects tenant isolation.

---

## 2. Preserve original values and normalize only for matching

**Decision:**  
Store the original CSV IDs and values while generating normalized references only for reconciliation.

**Alternative rejected:**  
Rewrite imported IDs and values into normalized forms before storing them.

**Reasoning:**  
Preserving the original source values makes discrepancies auditable and avoids losing information from the original exports.

---

## 3. Import dirty rows instead of silently rejecting them

**Decision:**  
Import every CSV row and store values defensively as strings, including blank and non-standard values.

**Alternative rejected:**  
Perform strict validation and skip rows that contain invalid values.

**Reasoning:**  
The assignment explicitly requires the importer to survive dirty data without silently dropping rows.

---

## 4. Use the location file as the tenant mapping source

**Decision:**  
Build the location-to-organization mapping from `locations.csv` before importing System A and System B.

**Alternative rejected:**  
Infer the organization directly from System A or System B records.

**Reasoning:**  
The assignment states that `locations.csv` is the source of truth for the relationship between locations and tenants.

---

## 5. Treat duplicate System B entries as a separate discrepancy

**Decision:**  
When more than one System B entry references the same record within the same organization, report a `DUPLICATE_IN_SYSTEM_B` discrepancy.

**Alternative rejected:**  
Choose the first System B entry and ignore the remaining entries.

**Reasoning:**  
Selecting one duplicate would hide a source-data problem and could produce an incorrect reconciliation result.

---

## 6. Compare System A total_value with System B value

**Decision:**  
Compare System A `total_value` against System B `value` for the primary numeric reconciliation.

**Alternative rejected:**  
Compare another System A numeric field such as `base_value`.

**Reasoning:**  
`total_value` represents the closest equivalent final value to System B's `value` in the supplied dataset.

---

## 7. Use Decimal for numeric comparison

**Decision:**  
Normalize numeric values and compare them using Python's `Decimal` rather than floating-point numbers.

**Alternative rejected:**  
Convert values directly to `float`.

**Reasoning:**  
Currency-like values can contain commas, currency symbols, and decimal precision. `Decimal` avoids floating-point precision issues and allows values such as `1,25,400.00` to be compared safely.

---

## 8. Treat date differences as VALUE_MISMATCH

**Decision:**  
Compare System A `event_date` with System B `recorded_on` and report differences using `VALUE_MISMATCH`.

**Alternative rejected:**  
Create a separate `DATE_MISMATCH` discrepancy type.

**Reasoning:**  
The assignment requires value discrepancies including dates while also defining a small set of discrepancy categories, so using the existing mismatch category keeps the API and UI simple.

---

## 9. Enforce tenant isolation at the API query layer

**Decision:**  
Require `org_id` for discrepancy requests and filter System A and System B database querysets by the selected organization before comparison.

**Alternative rejected:**  
Load records from all organizations and filter the results only in the React frontend.

**Reasoning:**  
Tenant isolation must be enforced on the backend. Filtering only in the frontend could expose another tenant's data to the browser.

---

## 10. Keep reconciliation logic separate from the API layer

**Decision:**  
Implement reconciliation in `services/comparator.py` and keep HTTP handling in `views.py`.

**Alternative rejected:**  
Put all comparison logic directly inside the Django API view.

**Reasoning:**  
Separating business logic from HTTP handling makes the comparison engine easier to test, understand, and maintain.