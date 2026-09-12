from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Organization, SystemARecord, SystemBEntry
from .services.comparator import (
    reconcile_records,
    safe_parse_decimal,
)


@require_GET
def organizations(request):
    data = [
        {
            "id": org.id,
            "code": org.code,
            "name": org.name,
        }
        for org in Organization.objects.all().order_by("code")
    ]

    return JsonResponse(data, safe=False)


@require_GET
def discrepancies(request):
    org_id = request.GET.get("org_id")
    reason = request.GET.get("reason")
    sort = request.GET.get("sort", "asc")

    if not org_id:
        return JsonResponse(
            {"error": "org_id is required"},
            status=400,
        )

    try:
        organization = Organization.objects.get(id=org_id)
    except Organization.DoesNotExist:
        return JsonResponse(
            {"error": "Organization not found"},
            status=404,
        )

    # Scope records to the selected organization before comparison.
    records_a_qs = (
        SystemARecord.objects
        .filter(location__organization=organization)
        .select_related("location", "location__organization")
    )

    records_b_qs = (
        SystemBEntry.objects
        .filter(location__organization=organization)
        .select_related("location", "location__organization")
    )

    records_a = [
        {
            "record_id": record.record_id,
            "location_id": record.location.external_id
            if record.location
            else None,
            "total_value": record.total_value,
            "event_date": record.event_date,
        }
        for record in records_a_qs
    ]

    records_b = [
        {
            "entry_id": entry.entry_id,
            "record_ref": entry.record_ref,
            "location_id": entry.location.external_id
            if entry.location
            else None,
            "value": entry.value,
            "recorded_on": entry.recorded_on,
        }
        for entry in records_b_qs
    ]

    location_org_map = {
        location.external_id: location.organization.code
        for location in organization.locations.all()
    }

    results = reconcile_records(
        records_a,
        records_b,
        location_org_map,
    )

    if reason:
        results = [
            item
            for item in results
            if item.reason == reason
        ]

    def sort_key(item):
        value = item.val_a if item.val_a not in (None, "") else item.val_b

        number = safe_parse_decimal(value)

        if number is not None:
            return (0, number)

        return (1, str(value or "").lower())

    results.sort(
        key=sort_key,
        reverse=sort.lower() == "desc",
    )

    data = [
        {
            "reason": item.reason,
            "record_id": item.record_id,
            "location_id": item.location_id,
            "org_id": item.org_id,
            "val_a": item.val_a,
            "val_b": item.val_b,
        }
        for item in results
    ]

    return JsonResponse(data, safe=False)