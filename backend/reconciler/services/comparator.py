import re
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


MISSING = "MISSING_IN_SYSTEM_B"
ORPHAN = "ORPHAN_IN_SYSTEM_B"
DUPLICATE = "DUPLICATE_IN_SYSTEM_B"
MISMATCH = "VALUE_MISMATCH"


@dataclass(frozen=True)
class Discrepancy:
    reason: str
    record_id: str
    location_id: str | None
    org_id: str
    val_a: str | None
    val_b: str | None


def normalize_reference(value: str | None) -> str:
    if value is None:
        return ""

    return re.sub(
        r"[^a-zA-Z0-9]",
        "",
        str(value),
    ).lower()


def safe_parse_decimal(value: str | None):
    if value is None:
        return None

    text = str(value).strip()

    if not text or text.upper() in {
        "N/A",
        "NULL",
        "NONE",
        "-",
    }:
        return None

    cleaned = re.sub(
        r"[^0-9.\-]",
        "",
        text,
    )

    if cleaned in {
        "",
        "-",
        ".",
        "-.",
    }:
        return None

    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def values_equal(a, b) -> bool:
    decimal_a = safe_parse_decimal(a)
    decimal_b = safe_parse_decimal(b)

    if decimal_a is not None and decimal_b is not None:
        return decimal_a == decimal_b

    return str(a or "").strip() == str(b or "").strip()


def reconcile_records(records_a, records_b, location_org_map):
    """
    Reconcile System A and System B using:

        (organization, normalized_record_id)

    as the matching key.

    This prevents records from different tenants from matching
    accidentally.

    System A:
        total_value is compared with System B value.
        event_date is compared with System B recorded_on.

    Raw values are preserved in the returned discrepancy.
    """

    # ---------------------------------------------------------
    # Build System A lookup
    # ---------------------------------------------------------

    a_by_key = {}

    for record in records_a:
        location_id = record.get("location_id")

        org_id = location_org_map.get(
            location_id,
            "UNKNOWN",
        )

        normalized_id = normalize_reference(
            record.get("record_id")
        )

        key = (
            org_id,
            normalized_id,
        )

        a_by_key[key] = record

    # ---------------------------------------------------------
    # Build System B lookup
    # ---------------------------------------------------------

    b_by_key = defaultdict(list)

    for record in records_b:
        location_id = record.get("location_id")

        org_id = location_org_map.get(
            location_id,
            "UNKNOWN",
        )

        normalized_ref = normalize_reference(
            record.get("record_ref")
        )

        if normalized_ref:
            key = (
                org_id,
                normalized_ref,
            )

            b_by_key[key].append(record)

    discrepancies = []

    # ---------------------------------------------------------
    # Pass 1, 2 and 4:
    # Duplicate, Missing, and Value/Date mismatch
    # ---------------------------------------------------------

    for key, record_a in a_by_key.items():

        org_id, normalized_id = key

        matching_b = b_by_key.get(
            key,
            [],
        )

        # -----------------------------------------------------
        # Missing in System B
        # -----------------------------------------------------

        if not matching_b:
            discrepancies.append(
                Discrepancy(
                    reason=MISSING,
                    record_id=record_a.get("record_id"),
                    location_id=record_a.get("location_id"),
                    org_id=org_id,
                    val_a=record_a.get("total_value"),
                    val_b=None,
                )
            )

            continue

        # -----------------------------------------------------
        # Duplicate in System B
        # -----------------------------------------------------

        if len(matching_b) > 1:

            values = "; ".join(
                str(entry.get("value", ""))
                for entry in matching_b
            )

            discrepancies.append(
                Discrepancy(
                    reason=DUPLICATE,
                    record_id=record_a.get("record_id"),
                    location_id=record_a.get("location_id"),
                    org_id=org_id,
                    val_a=record_a.get("total_value"),
                    val_b=values,
                )
            )

            continue

        # -----------------------------------------------------
        # Exactly one System B match
        # -----------------------------------------------------

        record_b = matching_b[0]

        value_mismatch = not values_equal(
            record_a.get("total_value"),
            record_b.get("value"),
        )

        date_mismatch = (
            str(record_a.get("event_date", "")).strip()
            != str(record_b.get("recorded_on", "")).strip()
        )

        # -----------------------------------------------------
        # Value mismatch
        # -----------------------------------------------------

        if value_mismatch:

            discrepancies.append(
                Discrepancy(
                    reason=MISMATCH,
                    record_id=record_a.get("record_id"),
                    location_id=record_a.get("location_id"),
                    org_id=org_id,
                    val_a=record_a.get("total_value"),
                    val_b=record_b.get("value"),
                )
            )

        # -----------------------------------------------------
        # Date mismatch
        #
        # The assignment treats dates as a payload value.
        # Display the dates as the compared values so the
        # discrepancy is visible in the UI.
        # -----------------------------------------------------

        if date_mismatch:

            discrepancies.append(
                Discrepancy(
                    reason=MISMATCH,
                    record_id=record_a.get("record_id"),
                    location_id=record_a.get("location_id"),
                    org_id=org_id,
                    val_a=record_a.get("event_date"),
                    val_b=record_b.get("recorded_on"),
                )
            )

    # ---------------------------------------------------------
    # Pass 3:
    # Orphan entries in System B
    # ---------------------------------------------------------

    for key, entries in b_by_key.items():

        if key not in a_by_key:

            for record_b in entries:

                org_id, normalized_ref = key

                discrepancies.append(
                    Discrepancy(
                        reason=ORPHAN,
                        record_id=record_b.get("record_ref"),
                        location_id=record_b.get("location_id"),
                        org_id=org_id,
                        val_a=None,
                        val_b=record_b.get("value"),
                    )
                )

    return discrepancies