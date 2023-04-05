from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ParseError
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Task, SubTask
from .serializers import TaskSerializer, SubTaskSerializer
from django.shortcuts import get_object_or_404


class Tasks(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_task = Task.objects.all()
        serializer = TaskSerializer(all_task, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save(
                create_user=request.user,
                team=request.data.get("team"),
                subtasks=request.data.get("subtasks"),
            )
            return Response(TaskSerializer(task).data)
        else:
            return Response(serializer.errors, status=400)


class TaskDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        # 업무(Task)는 작성자 이외에 수정이 불가합니다.
        if task.create_user != request.user:
            raise PermissionDenied
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            # 업무(Task)에 할당된 하위업무(SubTask)의 팀(Team)은 수정, 변경 가능해야 합니다
            new_task = serializer.save(
                team=request.data.get("team"),
                subtasks=request.data.get("subtasks"),
            )
            return Response(TaskSerializer(new_task).data)
        else:
            return Response(serializer.errors, status=400)


class MyTasks(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 업무(Task) 조회 시 하위업무(SubTask)에 본인 팀이 포함되어 있다면 업무목록에서 함께 조회가 가능해야합니다.
        # 업무(Task) 조회 시 하위업무(SubTask)의 업무 처리여부를 확인할 수 있어야 합니다.
        tasks = (
            Task.objects.filter(
                Q(team=request.user.team) | Q(subtasks__team=request.user.team)
            )
            .distinct()
            .order_by("created_at")
        )

        is_complete = request.GET.get("is_complete")

        if is_complete:
            if is_complete.lower() == "true":
                is_complete = True
            elif is_complete.lower() == "false":
                is_complete = False
            else:
                raise ParseError("is_complete parameter must be 'true' or 'false'")
            tasks = tasks.filter(is_complete=is_complete)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class MyMainTasks(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(team=request.user.team)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class MySubTasks(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(subtasks__team=request.user.team)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class SubTasksDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        subtask = get_object_or_404(SubTask, pk=pk)
        serializer = SubTaskSerializer(subtask)
        return Response(serializer.data)

    def put(self, request, pk):
        subtask = get_object_or_404(SubTask, pk=pk)
        # 하위업무(SubTask) 완료 처리는 소속된 팀만 처리 가능합니다.
        if subtask.team != request.user.team:
            raise PermissionDenied
        serializer = SubTaskSerializer(subtask, data=request.data, partial=True)
        if serializer.is_valid():
            new_sub_task = serializer.save()
            return Response(SubTaskSerializer(new_sub_task).data)
        else:
            return Response(serializer.errors, status=400)
