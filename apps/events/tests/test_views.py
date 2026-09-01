from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

class EventListTests(APITestCase):
    def test_list_events_public(self):
        response = self.client.get("/api/v1/events/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")