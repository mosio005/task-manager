
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from tasks.models import Task

User = get_user_model()


class BaseTaskTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='12345678'
        )

        self.other_user = User.objects.create_user(
            username='otheruser',
            password='12345678'
        )

        self.third_user = User.objects.create_user(
            username='thirduser',
            password='12345678'
        )

        self.task1 = Task.objects.create(
            title='My first task',
            owner=self.user,
            priority='high',
            status='todo'
        )

        self.task2 = Task.objects.create(
            title='Other user task',
            owner=self.other_user,
            priority='low',
            status='todo'
        )

        self.task3 = Task.objects.create(
            title='Buy something',
            description='Buy milk and bread',
            owner=self.user,
            priority='medium',
            status='in_progress'
        )

        self.expired_task = Task.objects.create(
            title='Expired task',
            owner=self.user,
            priority='high',
            status='todo',
            due_date=timezone.localdate() - timedelta(days=2)
        )

        self.done_task = Task.objects.create(
            title='Completed task',
            owner=self.user,
            priority='low',
            status='done'
        )
