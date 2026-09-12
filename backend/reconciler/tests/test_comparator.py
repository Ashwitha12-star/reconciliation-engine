from django.test import SimpleTestCase

from reconciler.services.comparator import (
    DUPLICATE,
    MISMATCH,
    MISSING,
    ORPHAN,
    reconcile_records,
)


class ComparatorTests(SimpleTestCase):

    def test_detects_record_missing_in_system_b(self):
        records_a = [
            {
                "record_id": "REC-001",
                "location_id": "LOC-101",
                "total_value": "100.00",
                "event_date": "2026-03-31",
            }
        ]

        records_b = []

        result = reconcile_records(
            records_a,
            records_b,
            {"LOC-101": "ORG-A"},
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].reason, MISSING)
        self.assertEqual(result[0].record_id, "REC-001")
        self.assertEqual(result[0].org_id, "ORG-A")
        self.assertEqual(result[0].val_a, "100.00")
        self.assertIsNone(result[0].val_b)

    def test_detects_orphan_record_in_system_b(self):
        records_a = []

        records_b = [
            {
                "record_ref": "REC-002",
                "location_id": "LOC-101",
                "value": "200.00",
                "recorded_on": "2026-03-31",
            }
        ]

        result = reconcile_records(
            records_a,
            records_b,
            {"LOC-101": "ORG-A"},
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].reason, ORPHAN)
        self.assertEqual(result[0].record_id, "REC-002")
        self.assertEqual(result[0].org_id, "ORG-A")
        self.assertIsNone(result[0].val_a)
        self.assertEqual(result[0].val_b, "200.00")

    def test_detects_duplicate_entries_in_system_b(self):
        records_a = [
            {
                "record_id": "REC-003",
                "location_id": "LOC-101",
                "total_value": "300.00",
                "event_date": "2026-03-31",
            }
        ]

        records_b = [
            {
                "record_ref": "REC-003",
                "location_id": "LOC-101",
                "value": "300.00",
                "recorded_on": "2026-03-31",
            },
            {
                "record_ref": "REC-003",
                "location_id": "LOC-101",
                "value": "300.00",
                "recorded_on": "2026-03-31",
            },
        ]

        result = reconcile_records(
            records_a,
            records_b,
            {"LOC-101": "ORG-A"},
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].reason, DUPLICATE)
        self.assertEqual(result[0].record_id, "REC-003")
        self.assertEqual(result[0].org_id, "ORG-A")
        self.assertEqual(result[0].val_a, "300.00")
        self.assertEqual(result[0].val_b, "300.00; 300.00")

    def test_detects_value_mismatch(self):
        records_a = [
            {
                "record_id": "REC-004",
                "location_id": "LOC-101",
                "total_value": "400.00",
                "event_date": "2026-03-31",
            }
        ]

        records_b = [
            {
                "record_ref": "REC-004",
                "location_id": "LOC-101",
                "value": "450.00",
                "recorded_on": "2026-03-31",
            }
        ]

        result = reconcile_records(
            records_a,
            records_b,
            {"LOC-101": "ORG-A"},
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].reason, MISMATCH)
        self.assertEqual(result[0].record_id, "REC-004")
        self.assertEqual(result[0].val_a, "400.00")
        self.assertEqual(result[0].val_b, "450.00")

    def test_numeric_formatting_is_not_a_mismatch(self):
        records_a = [
            {
                "record_id": "REC-005",
                "location_id": "LOC-101",
                "total_value": "125400.00",
                "event_date": "2026-03-31",
            }
        ]

        records_b = [
            {
                "record_ref": "REC-005",
                "location_id": "LOC-101",
                "value": "1,25,400.00",
                "recorded_on": "2026-03-31",
            }
        ]

        result = reconcile_records(
            records_a,
            records_b,
            {"LOC-101": "ORG-A"},
        )

        self.assertEqual(len(result), 0)

    def test_tenant_boundary_isolation(self):
        records_a = [
            {
                "record_id": "REC-007",
                "location_id": "LOC-101",
                "total_value": "700.00",
                "event_date": "2026-03-31",
            }
        ]

        records_b = [
            {
                "record_ref": "REC-007",
                "location_id": "LOC-201",
                "value": "700.00",
                "recorded_on": "2026-03-31",
            }
        ]

        result = reconcile_records(
            records_a,
            records_b,
            {
                "LOC-101": "ORG-A",
                "LOC-201": "ORG-B",
            },
        )

        self.assertEqual(len(result), 2)

        reasons = [item.reason for item in result]

        self.assertIn(MISSING, reasons)
        self.assertIn(ORPHAN, reasons)

    def test_detects_date_mismatch(self):
        records_a = [
            {
                "record_id": "REC-006",
                "location_id": "LOC-101",
                "total_value": "100.00",
                "event_date": "2026-03-31",
            }
        ]

        records_b = [
            {
                "record_ref": "REC-006",
                "location_id": "LOC-101",
                "value": "100.00",
                "recorded_on": "2026-04-02",
            }
        ]

        result = reconcile_records(
            records_a,
            records_b,
            {"LOC-101": "ORG-A"},
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].reason, MISMATCH)
        self.assertEqual(result[0].val_a, "2026-03-31")
        self.assertEqual(result[0].val_b, "2026-04-02")