
from rest_framework.test import APIClient

from .base import BaseTaskTestCase


class TaskFilterTests(BaseTaskTestCase):

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_filter_by_priority(self):
        response = self.client.get('/api/tasks/tasks/?priority=high')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)

        for task in response.data:
            self.assertEqual(task['priority'], 'high')

    def test_filter_by_status(self):
        response = self.client.get('/api/tasks/tasks/?status=todo')

        self.assertEqual(response.status_code, 200)

        for task in response.data:
            self.assertEqual(task['status'], 'todo')

    def test_filter_by_multiple_statuses(self):
        response = self.client.get(
            '/api/tasks/tasks/?status=todo,in_progress'
        )

        self.assertEqual(response.status_code, 200)

        for task in response.data:
            self.assertIn(
                task['status'],
                ['todo', 'in_progress']
            )

    def test_filter_expired_tasks(self):
        response = self.client.get(
            '/api/tasks/tasks/?is_expired=true'
        )

        self.assertEqual(response.status_code, 200)

        ids = [task['id'] for task in response.data]

        self.assertIn(self.expired_task.id, ids)

        for task in response.data:
            self.assertTrue(task['is_expired'])

    def test_filter_by_priority_and_status(self):
        response = self.client.get(
            '/api/tasks/tasks/?priority=high&status=todo'
        )

        self.assertEqual(response.status_code, 200)

        for task in response.data:
            self.assertEqual(task['priority'], 'high')
            self.assertEqual(task['status'], 'todo')

    def test_ordering_tasks_by_created_at(self):
        response = self.client.get(
            '/api/tasks/tasks/?ordering=-created_at'
        )

        self.assertEqual(response.status_code, 200)

        dates = [task['created_at'] for task in response.data]

        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_search_task_by_title(self):
        response = self.client.get(
            '/api/tasks/tasks/?search=Buy something'
        )

        self.assertEqual(response.status_code, 200)

        titles = [task['title'] for task in response.data]

        self.assertIn('Buy something', titles)

    def test_search_task_by_description(self):
        response = self.client.get(
            '/api/tasks/tasks/?search=milk'
        )

        self.assertEqual(response.status_code, 200)

        titles = [task['title'] for task in response.data]

        self.assertIn('Buy something', titles)

    def test_search_with_nonexistent_keyword(self):
        response = self.client.get(
            '/api/tasks/tasks/?search=nonexistentword'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

