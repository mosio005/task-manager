from rest_framework import serializers
from django.db import transaction
from django.utils import timezone

from .models import Task, TaskStatusHistory, TaskComment


class TaskSerializer(serializers.ModelSerializer):
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status' ,
            'priority', 'created_at', 'due_date', 
            'is_expired', 'updated_at'
        ]
        extra_kwargs = {
            'due_date':{'allow_null':True, 'required':False},
            'updated_at':{'read_only':True}
        }


    def validate_title(self, title):
        if not title.strip() :
            raise serializers.ValidationError(
                'the title is empty !!!'
            )
        return title


    def validate_due_date(self, due_date):
        if not due_date :
            return due_date
        
        if due_date < timezone.now().date():
            raise serializers.ValidationError(
                'the due date is expired '
            )
        return due_date


    def validate(self, attrs):

        if self.instance is None:
            return attrs


        allowed_transitions = {
            Task.StatusChoices.TODO : Task.StatusChoices.IN_PROGRESS,
            Task.StatusChoices.IN_PROGRESS : Task.StatusChoices.DONE
        }

        if self.instance.status == Task.StatusChoices.DONE:
            raise serializers.ValidationError(
            'Completed tasks cannot be edited.'
            )

        current_status = self.instance.status
        new_status = attrs.get('status', current_status)

        if current_status != new_status:
            if new_status != allowed_transitions.get(current_status):
                raise serializers.ValidationError({
                    'status':'Invalid status transition'
                })

        return attrs


    def update(self, instance, validated_data):
        with transaction.atomic():
            if 'status' in validated_data:
                if instance.status != validated_data['status']:
                    TaskStatusHistory.objects.create(
                        task=instance,
                        old_status=instance.status,
                        new_status=validated_data['status'],
                        user=self.context['request'].user
                    )

            return super().update(instance, validated_data)


class TaskStatusHistorySerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(
        source='task.title',
        read_only=True
    )

    user_name = serializers.CharField(
        source='user.username',
        read_only=True
    )

    class Meta:
        model = TaskStatusHistory
        fields = [
            'id',
            'task_title',
            'user_name',
            'old_status',
            'new_status',
            'changed_at'
        ]
        
        read_only_fields = fields



class TaskCommentSerializer(serializers.ModelSerializer):

    task_id = serializers.PrimaryKeyRelatedField(
        source='task',
        queryset=Task.objects.all(),
        write_only=True
    )

    user_username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    task_title = serializers.CharField(
        source='task.title',
        read_only=True
    )

    class Meta:
        model = TaskComment
        fields = [
            'id',
            'text',
            'user',
            'task_id',
            'created_at',
            'user_username',
            'task_title'
        ]
        extra_kwargs = {
            'user': {'read_only': True},
            'created_at': {'read_only': True}
        }


    def validate_text(self, text):
        if not text.split():
            raise serializers.ValidationError(
                'the comment can not be empty'
            )
        return text.strip()
        