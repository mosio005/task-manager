from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model



from .models import Task

User = get_user_model()


class TaskTest(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='testuser', password='123456')
        self.other_user = User.objects.create_user(username='testuser2', password='1234567')
        self.other_user_2 = User.objects.create_user(username='testuser3', password='12345678')


        self.task1 = Task.objects.create(
            title='title1',
            owner=self.user,
            priority='high'
        )
        self.task3 = Task.objects.create(
            title='title6',
            owner=self.other_user,
            priority='high'
        )

        self.task4 = Task.objects.create(
            title='title4',
            owner=self.other_user,
            priority='medium',
            due_date="2026-10-10"
        )


        self.task5 = Task.objects.create(
            title='title5',
            owner=self.other_user,
            priority='high',
            description='buy somthing'
        )


        self.task2 = Task.objects.create(
            title='title2',
            owner=self.other_user,
            priority='low',
        )


    def test_get_user_task(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.get('/api/tasks/tasks/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'title1')


    def test_user_edit_other_user_task(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.patch(
            f'/api/tasks/tasks/{self.task2.id}/',
            {'status':'done'},
            format='json'
        )

        self.assertEqual(response.status_code, 404)


    def test_user_create_task(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post(
            '/api/tasks/tasks/',
            {
                'title':'title3',
                'owner':self.other_user.id,
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            Task.objects.filter(title='title3').exists()
        )

        new_task = Task.objects.get(title='title3')
        self.assertEqual(new_task.owner, self.user)


    def test_create_task_with_empty_title(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        task_count = Task.objects.count()

        response = client.post(
            '/api/tasks/tasks/',
            {
                'title':'',
                'description':'description test',
                'owner':self.user.id,
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
    
        self.assertEqual(Task.objects.count(), task_count)
        


    def test_invalid_task_status_transition(self):
        client = APIClient()
        client.force_authenticate(user=self.user)   
        before_status = self.task1.status
        response = client.patch(
            f'/api/tasks/tasks/{self.task1.id}/status_update/',
            {
                'status':'done'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)

        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, before_status)



    def test_valid_task_status_transition(self):
        client = APIClient()
        client.force_authenticate(user=self.user)   

        response = client.patch(
            f'/api/tasks/tasks/{self.task1.id}/status_update/',
            {
                'status':'in_progress'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'in_progress')

        response = client.patch(
            f'/api/tasks/tasks/{self.task1.id}/status_update/',
            {
                'status':'done'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'done')




    def test_unauthenticated_user_cannot_create_tasks(self):
        client = APIClient()
        response = client.post(
            '/api/tasks/tasks/',
            {
                'title':'title3',
                'owner':self.user.id,
            },
            format='json'
        )

        self.assertEqual(response.status_code, 401)

        self.assertFalse(
            Task.objects.filter(title='title3').exists()
        )




    def test_query_filter(self):
        client = APIClient()
        client.force_authenticate(user=self.other_user)
        response = client.get(
            '/api/tasks/tasks/?priority=high'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)

        for task in response.data:
            self.assertEqual(task['priority'], 'high')


    def test_query_ordering_filter(self):
        client = APIClient()
        client.force_authenticate(user=self.other_user)
        response = client.get(
            '/api/tasks/tasks/?ordering=-created_at'
        )

        task1 = response.data[0]
        task2 = response.data[1]
        
        self.assertEqual(response.status_code, 200) 
        self.assertGreater(task1['created_at'], task2['created_at'])



    def test_expired_task(self):
        client = APIClient()
        client.force_authenticate(user=self.other_user)
        response = client.get(
            '/api/tasks/tasks/?is_expired=True'
        )

        self.assertEqual(response.status_code, 200) 




    def test_search_task(self):
        client = APIClient()
        client.force_authenticate(user=self.other_user)
        response = client.get(
            '/api/tasks/tasks/?search=buy'        
        )       

        self.assertEqual(response.status_code, 200) 

        