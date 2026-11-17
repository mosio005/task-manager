from django.db import models
from django.conf import settings


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks'    
    )

    class StatusChoices(models.TextChoices):
         
        TODO = 'todo'
        DONE = 'done'
        IN_PROGRESS = 'in_progress'
    
    status = models.CharField(
        max_length=12,
        choices=StatusChoices.choices,
        default=StatusChoices.TODO
    )


    class PriorityChoices(models.TextChoices):
             
            HIGH = 'high'
            MEDIUM = 'medium'
            LOW = 'low'
        
    priority = models.CharField(
        max_length=6, 
        choices=PriorityChoices.choices, 
        default=PriorityChoices.MEDIUM
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)


    def __str__(self):
        return self.title



class TaskStatusHistory(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='task_history',
    )

    old_status = models.CharField(
        max_length=15,
        choices=Task.StatusChoices.choices
    )

    new_status = models.CharField(
        max_length=15,
        choices=Task.StatusChoices.choices
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='status_changes'
    )

    changed_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.task.title}: {self.old_status} -> {self.new_status}'
    



class TaskComment(models.Model):
    text = models.TextField(null=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_comments',
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='task_comments'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.text[:30]}'
