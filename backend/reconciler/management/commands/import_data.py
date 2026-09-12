import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from reconciler.models import (
    Organization,
    Location,
    SystemARecord,
    SystemBEntry,
)
from reconciler.services.comparator import normalize_reference


ROOT = Path(__file__).resolve().parents[4]


def pick(row, *names):
    """
    Return the first matching CSV column value.

    Matching is case-insensitive and ignores surrounding whitespace.
    """
    normalized = {
        str(key).strip().lower(): (value or "").strip()
        for key, value in row.items()
    }

    for name in names:
        value = normalized.get(name.lower())
        if value is not None:
            return value

    return ""


class Command(BaseCommand):
    help = (
        "Import locations.csv, system_a.csv and system_b.csv "
        "without silently dropping dirty rows."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-dir",
            default=str(ROOT / "data"),
        )

    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"])

        locations_file = data_dir / "locations.csv"
        system_a_file = data_dir / "system_a.csv"
        system_b_file = data_dir / "system_b.csv"

        # Clear previously imported data so every import represents
        # the current CSV files.
        SystemARecord.objects.all().delete()
        SystemBEntry.objects.all().delete()
        Location.objects.all().delete()
        Organization.objects.all().delete()

        # ---------------------------------------------------------
        # 1. Import locations first so every event can be mapped
        #    to its organization/tenant.
        # ---------------------------------------------------------

        locations = {}

        with open(
            locations_file,
            newline="",
            encoding="utf-8-sig",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                location_id = pick(
                    row,
                    "location_id",
                    "location",
                    "id",
                )

                org_id = pick(
                    row,
                    "org_id",
                    "organization_id",
                    "organization",
                    "tenant_id",
                    "tenant",
                ) or "UNKNOWN"

                location_name = pick(
                    row,
                    "location_name",
                    "name",
                )

                if not location_id:
                    location_id = f"UNKNOWN-{len(locations) + 1}"

                organization, _ = Organization.objects.get_or_create(
                    code=org_id,
                    defaults={
                        "name": org_id,
                    },
                )

                location, _ = Location.objects.get_or_create(
                    external_id=location_id,
                    organization=organization,
                    defaults={
                        "name": location_name,
                    },
                )

                locations[location_id] = location

        # ---------------------------------------------------------
        # 2. Import System A
        # ---------------------------------------------------------

        a_count = 0

        with open(
            system_a_file,
            newline="",
            encoding="utf-8-sig",
        ) as file:
            reader = csv.DictReader(file)

            for row_number, row in enumerate(reader, start=2):
                record_id = pick(
                    row,
                    "record_id",
                    "id",
                    "record",
                )

                location_id = pick(
                    row,
                    "location_id",
                    "location",
                )

                SystemARecord.objects.create(
                    record_id=record_id,
                    normalized_record_id=normalize_reference(
                        record_id
                    ),
                    location=locations.get(location_id),
                    event_date=pick(
                        row,
                        "event_date",
                        "date",
                    ),
                    category_code=pick(
                        row,
                        "category_code",
                        "category",
                    ),
                    actor_id=pick(
                        row,
                        "actor_id",
                        "actor",
                    ),
                    base_value=pick(
                        row,
                        "base_value",
                    ),
                    adjustment=pick(
                        row,
                        "adjustment",
                    ),
                    total_value=pick(
                        row,
                        "total_value",
                        "value",
                        "amount",
                        "count",
                        "quantity",
                    ),
                    state=pick(
                        row,
                        "state",
                        "status",
                    ),
                    row_number=row_number,
                )

                a_count += 1

        # ---------------------------------------------------------
        # 3. Import System B
        # ---------------------------------------------------------

        b_count = 0

        with open(
            system_b_file,
            newline="",
            encoding="utf-8-sig",
        ) as file:
            reader = csv.DictReader(file)

            for row_number, row in enumerate(reader, start=2):
                record_ref = pick(
                    row,
                    "record_ref",
                    "record_id",
                    "reference",
                    "ref",
                )

                location_id = pick(
                    row,
                    "location_id",
                    "location",
                )

                SystemBEntry.objects.create(
                    entry_id=pick(
                        row,
                        "entry_id",
                        "id",
                    ),
                    record_ref=record_ref,
                    normalized_record_ref=normalize_reference(
                        record_ref
                    ),
                    location=locations.get(location_id),
                    recorded_on=pick(
                        row,
                        "recorded_on",
                        "date",
                    ),
                    value=pick(
                        row,
                        "value",
                        "amount",
                        "count",
                        "quantity",
                    ),
                    label=pick(
                        row,
                        "label",
                    ),
                    row_number=row_number,
                )

                b_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {a_count} System A rows and "
                f"{b_count} System B rows. "
                "No malformed rows were rejected."
            )
        )