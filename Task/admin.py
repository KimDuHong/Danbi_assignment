from django.contrib import admin
from .models import Task, SubTask


class SubTaskInline(admin.StackedInline):
    model = SubTask
    classes = ["collapse"]


# Register your models here.
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "create_user",
        "team",
        "subtasks",
        "title",
        "is_complete",
        "completed_date",
    )

    def subtasks(self, obj):
        if obj.subtasks:
            return ", ".join([subtask.team.name for subtask in obj.subtasks.all()])
        else:
            return ""

    subtasks.short_description = "Subtasks"

    inlines = [SubTaskInline]


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "task",
        "team",
        "is_complete",
        "completed_date",
    )
