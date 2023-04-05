# 업무(Task)의 모든 하위업무(SubTask)가 완료되면 해당 상위업무(Task)는 자동으로 완료처리가 되어야합니다.
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task, SubTask


@receiver(post_save, sender=SubTask)
def complete_parent_task(sender, instance, **kwargs):
    parent_task = instance.task
    all_subtasks_complete = parent_task.subtasks.filter(is_complete=False).exists()
    if not all_subtasks_complete:
        parent_task.is_complete = True
        parent_task.save()
