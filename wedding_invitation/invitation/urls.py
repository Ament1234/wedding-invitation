from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Wedding details (public landing) / Guest dashboard (admin)
    path('details/', views.details, name='details'),
    path('guest-list/', views.guest_list_dashboard, name='guest_list_dashboard'),

    # Admin actions
    path('guest-list/export/csv/', views.guest_list_export_csv, name='guest_list_export_csv'),
    path('guest-list/<int:pk>/delete/', views.guest_list_delete, name='guest_list_delete'),
    path('guest-list/<int:pk>/edit/', views.guest_list_edit, name='guest_list_edit'),

    # RSVP public
    path('rsvp/', views.rsvp, name='rsvp'),
    path('rsvp/submit/', views.rsvp_submit, name='rsvp_submit'),
    path('video/', views.video, name='video'),
]






