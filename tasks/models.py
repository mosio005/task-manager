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