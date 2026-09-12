from django.db import models


class Organization(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.code


class Location(models.Model):
    external_id = models.CharField(max_length=100)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="locations",
    )
    name = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ("external_id", "organization")

    def __str__(self):
        return self.external_id


class SystemARecord(models.Model):
    record_id = models.CharField(max_length=200)
    normalized_record_id = models.CharField(max_length=200, db_index=True)

    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    event_date = models.CharField(max_length=100, blank=True)
    category_code = models.CharField(max_length=100, blank=True)
    actor_id = models.CharField(max_length=200, blank=True)

    base_value = models.CharField(max_length=200, blank=True)
    adjustment = models.CharField(max_length=200, blank=True)
    total_value = models.CharField(max_length=200, blank=True)

    state = models.CharField(max_length=100, blank=True)

    row_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.record_id


class SystemBEntry(models.Model):
    entry_id = models.CharField(max_length=200, blank=True)

    record_ref = models.CharField(max_length=200)
    normalized_record_ref = models.CharField(max_length=200, db_index=True)

    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    recorded_on = models.CharField(max_length=100, blank=True)
    value = models.CharField(max_length=200, blank=True)
    label = models.CharField(max_length=200, blank=True)

    row_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.record_ref