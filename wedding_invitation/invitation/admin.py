from django.contrib import admin
from django.db.models import Sum

from .models import RSVP


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = (
        "guest_name",
        "phone",
        "email",
        "num_guests",
        "food_preference",
        "attendance",
        "created_at",
    )
    list_filter = ("attendance", "food_preference", "created_at")
    search_fields = ("guest_name", "phone", "email", "personal_message")
    readonly_fields = ("created_at",)

    def get_queryset(self, request):
        return super().get_queryset(request)

    @admin.display(description="Total guests (Will Attend)")
    def total_guests_will_attend(self, obj=None):
        # This is a helper if you want to render totals somewhere custom.
        qs = RSVP.objects.filter(attendance="Will Attend")
        result = qs.aggregate(total=Sum("num_guests"))
        return result.get("total") or 0
