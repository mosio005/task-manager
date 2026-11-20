from django.db.models import Case, When, Value, Q, BooleanField
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.serializers import ValidationError

from django_filters.rest_framework import DjangoFilterBackend 

from .models import Task, TaskStatusHistory, TaskComment
from .serializers import TaskSerializer, TaskStatusHistorySerializer, TaskCommentSerializer
from .filters import TaskFilter
from .permissions import TaskOwner, CommentOwner

User = get_user_model()



class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, TaskOwner]
    queryset = Task.objects.all().select_related('owner')
    serializer_class = TaskSerializer

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter           
    ]

    
    filterset_class = TaskFilter

    search_fields = [
        'title',
        'description'
    ]

    ordering_fields = [
        'due_date',
        'created_at',
        'priority'
    ]

    ordering = ['-created_at']


    def get_queryset(self):
        queryset = self.queryset 

        queryset = queryset.filter(owner=self.request.user).annotate(
            is_expired=Case(
                When(
                    due_date__isnull=True, then=Value(False)
                ),

                When(
                    Q(due_date__lt=timezone.now().date()) & Q(status__in=('todo', 'in_progress')), 
                    then=Value(True)
                ),

                default=Value(False),
                output_field=BooleanField()
            )
        )
        return queryset


    def perform_create(self, serializer):
        with transaction.atomic():
            user = User.objects.select_for_update().get(id=self.request.user.id)
            if user.tasks.filter(status__in=('todo', 'in_progress')).count() >= 10:
                raise ValidationError(
                    'the maximum count of task for any user is 10 !!!'
                )

            serializer.save(
                owner=user
            )




    def perform_destroy(self, instance):
        if instance.status == Task.StatusChoices.DONE:
            raise ValidationError(
                'you cant delete task when the status of task is done'
            )
        return super().perform_destroy(instance)
        

    @action(methods=['PATCH'], detail=True)
    def status_update(self, request, pk=None):
        task = self.get_object()

        new_status = request.data.get('status')

        serializer = self.get_serializer(task, {'status': new_status}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'message':'status has been updated'},
            status=status.HTTP_200_OK
        )

    @action(methods=['GET'], detail=True)
    def task_status_history(self, request, pk=None):
        task = self.get_object()
        task_history = TaskStatusHistory.objects.filter(task=task).order_by('-changed_at')
        serializer = TaskStatusHistorySerializer(task_history, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


    @action(methods=['GET'], detail=True)
    def comments(self, request, pk=None):
        task = self.get_object()
        serializer = TaskCommentSerializer(
            TaskComment.objects.filter(
                task=task
            ).order_by('-created_at'),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )



class TaskCommentViewSet(viewsets.ModelViewSet):
    queryset = TaskComment.objects.all().select_related(
        'task', 'user'
    )
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated, CommentOwner]


    def get_queryset(self):
        queryset =  super().get_queryset()

        return queryset.filter(
            task__owner=self.request.user
        ).order_by('-created_at')

    def perform_create(self, serializer):
        if serializer.validated_data['task'].owner != self.request.user:
            raise ValidationError(
                'you cant creat comment on another users task'
            )

        serializer.save(
            user=self.request.user
        )
