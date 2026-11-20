
from rest_framework.test import APIClient

from .base import BaseTaskTestCase
from tasks.models import Task


class TaskViewSetTests(BaseTaskTestCase):

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_user_task(self):
        response = self.client.get('/api/tasks/tasks/')

        self.assertEqual(response.status_code, 200)

        titles = [task['title'] for task in response.data]

        self.assertIn(self.task1.title, titles)
        self.assertNotIn(self.task2.title, titles)

    def test_user_edit_other_user_task(self):
        response = self.client.patch(
            f'/api/tasks/tasks/{self.task2.id}/',
            {'title': 'Hacked title'},
            format='json'
        )

        self.assertEqual(response.status_code, 404)

        self.task2.refresh_from_db()
        self.assertEqual(self.task2.title, 'Other user task')

    def test_user_create_task(self):
        response = self.client.post(
            '/api/tasks/tasks/',
            {
                'title': 'New task',
                'priority': 'high'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)

        task = Task.objects.get(title='New task')
        self.assertEqual(task.owner, self.user)

    def test_create_task_with_empty_title(self):
        initial_count = Task.objects.count()

        response = self.client.post(
            '/api/tasks/tasks/',
            {
                'title': '   ',
                'priority': 'high'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Task.objects.count(), initial_count)

    def test_invalid_task_status_transition(self):
        response = self.client.patch(
            f'/api/tasks/tasks/{self.task1.id}/',
            {'status': 'done'},
            format='json'
        )

        self.assertEqual(response.status_code, 400)

        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'todo')

    def test_valid_task_status_transition(self):
        response = self.client.patch(
            f'/api/tasks/tasks/{self.task1.id}/',
            {'status': 'in_progress'},
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'in_progress')

        response = self.client.patch(
            f'/api/tasks/tasks/{self.task1.id}/',
            {'status': 'done'},
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'done')

    def test_unauthenticated_user_cannot_create_tasks(self):
        self.client.force_authenticate(user=None)

        initial_count = Task.objects.count()

        response = self.client.post(
            '/api/tasks/tasks/',
            {'title': 'Unauthorized task'},
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Task.objects.count(), initial_count)

    def test_cannot_delete_done_task(self):
        response = self.client.delete(
            f'/api/tasks/tasks/{self.done_task.id}/'
        )

        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            Task.objects.filter(id=self.done_task.id).exists()
        )

    def test_cannot_create_more_than_ten_active_tasks(self):
        for number in range(7):
            Task.objects.create(
                title=f'Extra task {number}',
                owner=self.user,
                status='todo'
            )

        response = self.client.post(
            '/api/tasks/tasks/',
            {'title': 'Eleventh active task'},
            format='json'
        )

        self.assertEqual(response.status_code, 400)
