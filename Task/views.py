from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ParseError
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from Team.models import Team
from .models import Task, SubTask
from .serializers import TaskSerializer, SubTaskSerializer


class Tasks(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="View all task",
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=TaskSerializer(many=True),
            ),
            403: openapi.Response(description="Forbidden Response"),
        },
    )
    def get(self, request):
        all_task = Task.objects.all()
        serializer = TaskSerializer(all_task, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Post new Task",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["title", "content"],
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="title"),
                "content": openapi.Schema(
                    type=openapi.TYPE_STRING, description="content"
                ),
                "team": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="업무를 배정할 팀, team 혹은 subtasks 중 하나는 반드시 존재해야함",
                    enum=Team.TeamChoices.values,
                ),
                "subtasks": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_STRING,
                        enum=Team.TeamChoices.values,
                    ),
                    description="보조 업무를 배정할 팀 리스트",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=TaskSerializer(),
            ),
            400: openapi.Response(description="Validate Error"),
            403: openapi.Response(description="Forbidden Response"),
        },
    )
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

    @swagger_auto_schema(
        operation_summary="View task detail",
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=TaskSerializer(),
            ),
            400: openapi.Response(description="Not Found PK"),
            403: openapi.Response(description="Forbidden Response"),
        },
    )
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="edit task detail",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="title"),
                "content": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="content",
                ),
                "is_complete": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="업무 완료 상태 변경",
                ),
                "team": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="업무를 배정할 팀, team 혹은 subtasks 중 하나는 반드시 존재해야함",
                    enum=Team.TeamChoices.values,
                ),
                "subtasks": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_STRING,
                        enum=Team.TeamChoices.values,
                    ),
                    description="보조 업무를 배정할 팀 리스트",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=TaskSerializer(),
            ),
            400: openapi.Response(description="Validate Error"),
            403: openapi.Response(description="Forbidden Response"),
            404: openapi.Response(description="Not Found PK"),
        },
    )
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

    @swagger_auto_schema(
        operation_summary="View my tasks",
        manual_parameters=[
            openapi.Parameter(
                "is_complete",
                openapi.IN_QUERY,
                description="작업완료 / 작업중 , 기본값 : 전부",
                type=openapi.TYPE_BOOLEAN,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=TaskSerializer(many=True),
            ),
            403: openapi.Response(description="Forbidden Response"),
        },
    )
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

    @swagger_auto_schema(
        operation_summary="View my main tasks",
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=TaskSerializer(many=True),
            ),
            403: openapi.Response(description="Forbidden Response"),
        },
    )
    def get(self, request):
        tasks = Task.objects.filter(team=request.user.team)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class MySubTasks(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="View my sub tasks",
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=TaskSerializer(many=True),
            ),
            403: openapi.Response(description="Forbidden Response"),
        },
    )
    def get(self, request):
        tasks = Task.objects.filter(subtasks__team=request.user.team)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class SubTasksDetail(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="View subtask detail",
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=SubTaskSerializer(),
            ),
            403: openapi.Response(description="Forbidden Response"),
        },
    )
    def get(self, request, pk):
        subtask = get_object_or_404(SubTask, pk=pk)
        serializer = SubTaskSerializer(subtask)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="edit subtask detail",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "is_complete": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="업무 완료 상태 변경",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Successful Response",
                schema=SubTaskSerializer(),
            ),
            400: openapi.Response(description="Validate Error"),
            403: openapi.Response(description="Forbidden Response"),
            404: openapi.Response(description="Not Found PK"),
        },
    )
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
