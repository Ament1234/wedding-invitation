from django.db import models


class RSVP(models.Model):
    ATTENDANCE_CHOICES = [
        ("Will Attend", "Will Attend"),
        ("Will Not Attend", "Will Not Attend"),
    ]

    guest_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    num_guests = models.PositiveIntegerField()
    food_preference = models.CharField(max_length=50)
    attendance = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES)

    personal_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.guest_name} ({self.attendance})"
