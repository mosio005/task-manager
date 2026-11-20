
from rest_framework.test import APIClient

from .base import BaseTaskTestCase
from tasks.models import TaskComment


class TaskCommentViewSetTests(BaseTaskTestCase):

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.comment = TaskComment.objects.create(
            text='My test comment',
            user=self.user,
            task=self.task1
        )

    def test_create_comment(self):
        response = self.client.post(
            '/api/tasks/comments/',
            {
                'text': 'A new comment',
                'task_id': self.task1.id
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)

        comment = TaskComment.objects.get(text='A new comment')
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.task, self.task1)

    def test_cannot_comment_on_other_user_task(self):
        initial_count = TaskComment.objects.count()

        response = self.client.post(
            '/api/tasks/comments/',
            {
                'text': 'Unauthorized comment',
                'task_id': self.task2.id
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(TaskComment.objects.count(), initial_count)

    def test_cannot_create_comment_without_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            '/api/tasks/comments/',
            {
                'text': 'Anonymous comment',
                'task_id': self.task1.id
            },
            format='json'
        )

        self.assertEqual(response.status_code, 401)

    def test_get_user_comments(self):
        response = self.client.get('/api/tasks/comments/')

        self.assertEqual(response.status_code, 200)

        ids = [item['id'] for item in response.data]
        self.assertIn(self.comment.id, ids)

    def test_update_own_comment(self):
        response = self.client.patch(
            f'/api/tasks/comments/{self.comment.id}/',
            {'text': 'Updated comment'},
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'Updated comment')

    def test_other_user_cannot_update_comment(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            f'/api/tasks/comments/{self.comment.id}/',
            {'text': 'Changed by another user'},
            format='json'
        )

        self.assertEqual(response.status_code, 404)

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'My test comment')

    def test_delete_own_comment(self):
        response = self.client.delete(
            f'/api/tasks/comments/{self.comment.id}/'
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            TaskComment.objects.filter(id=self.comment.id).exists()
        )

    def test_other_user_cannot_delete_comment(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(
            f'/api/tasks/comments/{self.comment.id}/'
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            TaskComment.objects.filter(id=self.comment.id).exists()
        )

    def test_create_comment_with_empty_text(self):
        initial_count = TaskComment.objects.count()

        response = self.client.post(
            '/api/tasks/comments/',
            {
                'text': '   ',
                'task_id': self.task1.id
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(TaskComment.objects.count(), initial_count)
