from django.db.models import Sum, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST


from .models import RSVP


def home(request):
    return render(request, 'invitation/home.html')


def details(request):
    return render(request, 'invitation/details.html')


def guest_list_dashboard(request):
    from django.core.paginator import Paginator
    from django.utils import timezone

    # Query params
    q = (request.GET.get('q') or '').strip()
    attendance_filter = request.GET.get('attendance') or 'all'
    food_filter = request.GET.get('food') or 'all'
    family_filter = request.GET.get('family') or 'all'
    sort = request.GET.get('sort') or 'latest'

    qs = RSVP.objects.all()

    # “Confirmed attendance” requirement: show Will Attend guests.
    qs = qs.filter(attendance='Will Attend')

    if q:
        qs = qs.filter(
            Q(guest_name__icontains=q)
            | Q(phone__icontains=q)
            | Q(email__icontains=q)
            | Q(personal_message__icontains=q)
        )

    if attendance_filter in ['Will Attend', 'Will Not Attend']:
        qs = qs.filter(attendance=attendance_filter)

    if food_filter == 'Vegetarian':
        qs = qs.filter(food_preference__icontains='veg') | qs.filter(food_preference__icontains='veg')

    elif food_filter == 'Non-Vegetarian':
        # crude but effective mapping for existing free-text field
        qs = qs.exclude(food_preference__icontains='veg')

    if family_filter != 'all':
        if family_filter == '1':
            qs = qs.filter(num_guests=1)
        elif family_filter == '2':
            qs = qs.filter(num_guests=2)
        elif family_filter == '3-4':
            qs = qs.filter(num_guests__gte=3, num_guests__lte=4)
        elif family_filter == '5plus':
            qs = qs.filter(num_guests__gte=5)

    if sort == 'name':
        qs = qs.order_by('guest_name')
    elif sort == 'num_desc':
        qs = qs.order_by('-num_guests', '-created_at')
    else:
        qs = qs.order_by('-created_at')

    # Stats are computed on the same base (confirmed attendees)
    base = RSVP.objects.filter(attendance='Will Attend')
    total_rsvp_responses = base.count()
    total_attending = base.aggregate(total=Sum('num_guests')).get('total') or 0
    total_not_attending = RSVP.objects.filter(attendance='Will Not Attend').aggregate(total=Sum('num_guests')).get('total') or 0
    total_family_members_coming = total_attending

    vegetarian_count = base.filter(food_preference__icontains='veg').count()
    non_vegetarian_count = base.exclude(food_preference__icontains='veg').count()

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'q': q,
        'attendance_filter': attendance_filter,
        'food_filter': food_filter,
        'family_filter': family_filter,
        'sort': sort,
        'today': timezone.now(),
        'total_rsvp_responses': total_rsvp_responses,
        'total_attending': total_attending,
        'total_not_attending': total_not_attending,
        'total_family_members_coming': total_family_members_coming,
        'vegetarian_count': vegetarian_count,
        'non_vegetarian_count': non_vegetarian_count,
    }
    return render(request, 'invitation/guest_list.html', context)


def guest_list_export_csv(request):
    import csv
    from django.http import HttpResponse

    attendance = request.GET.get('attendance') or 'Will Attend'
    qs = RSVP.objects.all()
    if attendance:
        qs = qs.filter(attendance=attendance)

    qs = qs.order_by('-created_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="guest_list.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Guest ID',
        'Guest Name',
        'Phone',
        'Email',
        'Number of People Coming',
        'Food Preference',
        'Attendance Status',
        'Personal Message',
        'Submission Date',
    ])

    for g in qs:
        writer.writerow([
            g.id,
            g.guest_name,
            g.phone,
            g.email,
            g.num_guests,
            g.food_preference,
            g.attendance,
            g.personal_message,
            g.created_at.isoformat(),
        ])

    return response


def guest_list_delete(request, pk):
    if request.method != 'POST':
        # simple guard; redirect back to dashboard
        from django.shortcuts import redirect
        return redirect('guest_list_dashboard')

    obj = RSVP.objects.filter(pk=pk).first()
    if obj:
        obj.delete()

    from django.shortcuts import redirect
    return redirect(request.GET.get('next') or 'guest_list_dashboard')


def guest_list_edit(request, pk):
    from django.shortcuts import get_object_or_404, redirect

    obj = get_object_or_404(RSVP, pk=pk)

    if request.method == 'POST':
        obj.guest_name = (request.POST.get('guest_name') or '').strip()
        obj.phone = (request.POST.get('phone') or '').strip()
        obj.email = (request.POST.get('email') or '').strip()
        obj.num_guests = int(request.POST.get('num_guests') or 0)
        obj.food_preference = (request.POST.get('food_preference') or '').strip()
        obj.attendance = request.POST.get('attendance')
        obj.personal_message = (request.POST.get('personal_message') or '').strip()
        obj.save()
        return redirect(request.GET.get('next') or 'guest_list_dashboard')

    # Minimal edit form: reuse a simple inline template via render with context.
    # If you want a full template later, we can add it.
    return render(request, 'invitation/guest_list_edit.html', {'obj': obj})



def rsvp(request):
    return render(request, 'invitation/rsvp.html')


def video(request):
    return render(request, 'invitation/video.html')


@require_POST
def rsvp_submit(request):
    # Expecting fields from rsvp.html
    guest_name = (request.POST.get("guest_name") or "").strip()
    phone = (request.POST.get("phone") or "").strip()
    email = (request.POST.get("email") or "").strip()
    attendance = (request.POST.get("attendance") or "").strip()
    personal_message = (request.POST.get("personal_message") or "").strip()
    num_guests_raw = request.POST.get("num_guests")
    food_preference = (request.POST.get("food_preference") or "").strip()

    try:
        num_guests = int(num_guests_raw)
    except (TypeError, ValueError):
        num_guests = 0

    if not guest_name or not phone or not email or attendance not in dict(RSVP.ATTENDANCE_CHOICES):
        return JsonResponse({"status": "error", "message": "Invalid RSVP data"}, status=400)

    if attendance == "Will Attend":
        if num_guests < 1 or not food_preference:
            return JsonResponse({"status": "error", "message": "Invalid RSVP data"}, status=400)
    else:
        num_guests = 0
        food_preference = ""

    rsvp_obj = RSVP.objects.create(
        guest_name=guest_name,
        phone=phone,
        email=email,
        num_guests=num_guests,
        food_preference=food_preference,
        attendance=attendance,
        personal_message=personal_message,
    )

    total = RSVP.objects.filter(attendance="Will Attend").aggregate(total=Sum("num_guests")).get("total") or 0

    return JsonResponse({"status": "success", "rsvp_id": rsvp_obj.id, "new_total_guests": total})


