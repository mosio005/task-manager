from django.contrib import admin
from .models import Task, TaskStatusHistory, TaskComment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'owner',
        'status',
        'priority',
        'due_date',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'status',
        'priority',
        'created_at',
        'due_date',
    )

    search_fields = (
        'title',
        'description',
        'owner__username',
    )

    ordering = ('-created_at',)

    readonly_fields = (
        'created_at',
        'updated_at',
    )


@admin.register(TaskStatusHistory)
class TaskStatusHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'task',
        'old_status',
        'new_status',
        'user',
        'changed_at',
    )

    list_filter = (
        'old_status',
        'new_status',
        'changed_at',
    )

    search_fields = (
        'task__title',
        'user__username',
    )

    ordering = ('-changed_at',)

    readonly_fields = (
        'changed_at',
    )


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'task',
        'user',
        'created_at',
    )

    list_filter = (
        'created_at',
    )

    search_fields = (
        'text',
        'task__title',
        'user__username',
    )

    ordering = ('-created_at',)

    readonly_fields = (
        'created_at',
    )
