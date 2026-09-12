from django.test import SimpleTestCase

from reconciler.services.comparator import (
    DUPLICATE,
    MISSING,
    MISMATCH,
    ORPHAN,
    reconcile_records,
)


class ComparatorTests(SimpleTestCase):

    def test_detects_record_missing_in_system_b(self):
        records_a = [
            {
                "record_id": "REC-01",
                "total_value": "100",
                "event_date": "2026-01-01",
                "location_id": "LOC-1",
            }
        ]

        records_b = []

        location_map = {
            "LOC-1": "ORG-1",
        }

        results = reconcile_records(
            records_a,
            records_b,
            location_map,
        )

        assert len(results) == 1
        assert results[0].reason == MISSING
        assert results[0].record_id == "REC-01"


    def test_detects_orphan_record_in_system_b(self):
        records_a = []

        records_b = [
            {
                "record_ref": "REC-999",
                "value": "250",
                "recorded_on": "2026-01-01",
                "location_id": "LOC-1",
            }
        ]

        location_map = {
            "LOC-1": "ORG-1",
        }

        results = reconcile_records(
            records_a,
            records_b,
            location_map,
        )

        assert len(results) == 1
        assert results[0].reason == ORPHAN
        assert results[0].record_id == "REC-999"


    def test_detects_duplicate_entries_in_system_b(self):
        records_a = [
            {
                "record_id": "REC-01",
                "total_value": "100",
                "event_date": "2026-01-01",
                "location_id": "LOC-1",
            }
        ]

        records_b = [
            {
                "record_ref": "REC-01",
                "value": "100",
                "recorded_on": "2026-01-01",
                "location_id": "LOC-1",
            },
            {
                "record_ref": " rec-01 ",
                "value": "100",
                "recorded_on": "2026-01-01",
                "location_id": "LOC-1",
            },
        ]

        location_map = {
            "LOC-1": "ORG-1",
        }

        results = reconcile_records(
            records_a,
            records_b,
            location_map,
        )

        assert any(
            result.reason == DUPLICATE
            for result in results
        )


    def test_detects_value_mismatch(self):
        records_a = [
            {
                "record_id": "REC-01",
                "total_value": "100.00",
                "event_date": "2026-01-01",
                "location_id": "LOC-1",
            }
        ]

        records_b = [
            {
                "record_ref": "REC-01",
                "value": "120.00",
                "recorded_on": "2026-01-01",
                "location_id": "LOC-1",
            }
        ]

        location_map = {
            "LOC-1": "ORG-1",
        }

        results = reconcile_records(
            records_a,
            records_b,
            location_map,
        )

        assert len(results) == 1
        assert results[0].reason == MISMATCH
        assert results[0].val_a == "100.00"
        assert results[0].val_b == "120.00"


    def test_numeric_formatting_is_not_a_mismatch(self):
        records_a = [
            {
                "record_id": "REC-01",
                "total_value": "100.00",
                "event_date": "2026-01-01",
                "location_id": "LOC-1",
            }
        ]

        records_b = [
            {
                "record_ref": "REC-01",
                "value": "$100.00",
                "recorded_on": "2026-01-01",
                "location_id": "LOC-1",
            }
        ]

        location_map = {
            "LOC-1": "ORG-1",
        }

        results = reconcile_records(
            records_a,
            records_b,
            location_map,
        )

        assert results == []


    def test_tenant_boundary_isolation(self):
        records_a = [
            {
                "record_id": "REC-01",
                "total_value": "100",
                "event_date": "2026-01-01",
                "location_id": "LOC-A",
            }
        ]

        records_b = [
            {
                "record_ref": "REC-01",
                "value": "100",
                "recorded_on": "2026-01-01",
                "location_id": "LOC-B",
            }
        ]

        location_map = {
            "LOC-A": "ORG-A",
            "LOC-B": "ORG-B",
        }

        results = reconcile_records(
            records_a,
            records_b,
            location_map,
        )

        assert any(
            result.reason == MISSING
            and result.org_id == "ORG-A"
            for result in results
        )

        assert any(
            result.reason == ORPHAN
            and result.org_id == "ORG-B"
            for result in results
        )