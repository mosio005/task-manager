
from rest_framework.test import APIClient

from .base import BaseTaskTestCase
from tasks.models import TaskStatusHistory


class TaskStatusHistoryTests(BaseTaskTestCase):

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_status_change_creates_history(self):
        response = self.client.patch(
            f'/api/tasks/tasks/{self.task1.id}/',
            {'status': 'in_progress'},
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        history = TaskStatusHistory.objects.filter(task=self.task1)

        self.assertEqual(history.count(), 1)

        record = history.first()
        self.assertEqual(record.old_status, 'todo')
        self.assertEqual(record.new_status, 'in_progress')
        self.assertEqual(record.user, self.user)

    def test_same_status_does_not_create_history(self):
        initial_count = TaskStatusHistory.objects.filter(
            task=self.task1
        ).count()

        response = self.client.patch(
            f'/api/tasks/tasks/{self.task1.id}/',
            {'title': 'Updated title'},
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        new_count = TaskStatusHistory.objects.filter(
            task=self.task1
        ).count()

        self.assertEqual(new_count, initial_count)

    def test_get_task_status_history(self):
        self.client.patch(
            f'/api/tasks/tasks/{self.task1.id}/',
            {'status': 'in_progress'},
            format='json'
        )

        response = self.client.get(
            f'/api/tasks/tasks/{self.task1.id}/task_status_history/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]['old_status'], 'todo')
        self.assertEqual(response.data[0]['new_status'], 'in_progress')

    def test_cannot_access_other_user_task_history(self):
        response = self.client.get(
            f'/api/tasks/tasks/{self.task2.id}/task_status_history/'
        )

        self.assertEqual(response.status_code, 404)
