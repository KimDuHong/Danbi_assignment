from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import SerializerMethodField
from .models import Task, SubTask
from User.serializers import TinyUserSerializer
from Team.serializers import TeamSerializer
from django.db import transaction
from rest_framework.exceptions import ParseError
from django.shortcuts import get_object_or_404
from Team.models import Team


class SubTaskSerializer(ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = SubTask
        fields = ("pk", "is_complete", "team")


class TaskSerializer(ModelSerializer):
    create_user = TinyUserSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    # 업무(Task) 조회 시 하위업무(SubTask)의 업무 처리여부를 확인할 수 있어야 합니다.
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = "__all__"

    def create(self, validated_data):
        subtasks_data = validated_data.pop("subtasks", None)
        team = validated_data.pop("team", None)
        if subtasks_data or team:
            with transaction.atomic():
                task = Task.objects.create(**validated_data)
                if team:
                    task.team = get_object_or_404(Team, name=team)
                if subtasks_data:
                    if not isinstance(subtasks_data, list):
                        raise ParseError("subtasks must be list")
                    for subtask_data in subtasks_data:
                        sub_team = get_object_or_404(Team, name=subtask_data)
                        SubTask.objects.create(task=task, team=sub_team)
            return task
        else:
            raise ParseError("최소 한개의 팀이 필요합니다.")

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.content = validated_data.get("content", instance.content)
        instance.is_complete = validated_data.get("is_complete", instance.is_complete)
        team = validated_data.get("team", instance.team and instance.team.name)
        if team:
            instance.team = get_object_or_404(Team, name=team)

        subtasks = validated_data.get("subtasks", instance.subtasks)
        if subtasks != None:
            if not isinstance(subtasks, list):
                raise ParseError("subtasks must be list")

            # 단 해당 하위업무(SubTask)가 완료되었다면 삭제되지 않아야 합니다.
            with transaction.atomic():
                current_subtasks = instance.subtasks.filter(is_complete=False)
                for subtask in current_subtasks:
                    subtask.delete()

                for subtask_data in subtasks:
                    sub_team = get_object_or_404(Team, name=subtask_data)
                    SubTask.objects.create(task=instance, team=sub_team)

                if instance.subtasks.count() == 0 and instance.team == None:
                    raise ParseError("최소 한개의 팀이 필요합니다.")

                instance.save()

        return instance
