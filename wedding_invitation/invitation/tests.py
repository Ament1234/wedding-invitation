from django.test import TestCase
from django.urls import reverse

from .models import RSVP


class RSVPSubmitTests(TestCase):
    def test_rsvp_submit_attending(self):
        response = self.client.post(
            reverse('rsvp_submit'),
            {
                'guest_name': 'Test Guest',
                'phone': '9876543210',
                'email': 'test@example.com',
                'num_guests': '2',
                'food_preference': 'Vegetarian',
                'attendance': 'Will Attend',
                'personal_message': 'Looking forward to the celebration!',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['new_total_guests'], 2)
        self.assertEqual(RSVP.objects.count(), 1)

    def test_rsvp_submit_not_attending(self):
        response = self.client.post(
            reverse('rsvp_submit'),
            {
                'guest_name': 'Test Guest',
                'phone': '9876543210',
                'email': 'test@example.com',
                'num_guests': '1',
                'food_preference': 'Vegetarian',
                'attendance': 'Will Not Attend',
                'personal_message': 'Sorry I cannot make it.',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['new_total_guests'], 0)
        self.assertEqual(RSVP.objects.count(), 1)
        rsvp = RSVP.objects.first()
        self.assertEqual(rsvp.num_guests, 0)
        self.assertEqual(rsvp.food_preference, '')
