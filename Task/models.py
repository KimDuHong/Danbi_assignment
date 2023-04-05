from django.db import models
from Common.models import CommonModel
from User.models import User
from Team.models import Team
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your models here.
class TaskStatusModel(models.Model):
    is_complete = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.is_complete and not self.completed_date:
            self.completed_date = timezone.localdate()
        elif not self.is_complete:
            self.completed_date = None
        super().save(*args, **kwargs)


class SubTask(TaskStatusModel, CommonModel):
    task = models.ForeignKey(
        "Task",
        on_delete=models.CASCADE,
        related_name="subtasks",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.task}'s subtask by {self.team}"

    def clean(self):
        super().clean()
        if self.team:
            if self.team.name not in Team.TeamChoices.values:
                raise ValidationError(
                    "Subtasks cannot be assigned to teams other than the 7 designated teams."
                )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Task(TaskStatusModel, CommonModel):
    create_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self) -> str:
        return f"{self.create_user}의 {self.title}"

    # def clean(self):
    #     super().clean()

    # # 업무 생성 시, 한 개 이상의 팀을 설정해야합니다.
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     if not self.team and not self.subtasks.exists():
    #         raise ValidationError("업무 생성 시, 한 개 이상의 팀을 설정해야합니다.")
