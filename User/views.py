from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import authenticate, login, logout
from .serializers import PrivateUserSerializer
from Team.models import Team
from django.shortcuts import get_object_or_404
from django.db import transaction
import re


class Login(APIView):
    @swagger_auto_schema(
        operation_summary="User Login",
        responses={200: "OK", 400: "name or password error"},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING, description="유저 id ( username )"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="유저 비밀번호"
                ),
            },
        ),
    )
    def post(self, request):
        username = str(request.data.get("username"))
        password = str(request.data.get("password"))
        if not username or not password:
            raise ParseError
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user:
            login(request, user)
            return Response("로그인 성공")
        else:
            return Response({"error": "wrong name or password"}, status=400)


class SignUp(APIView):
    def validate_password(self, password):
        REGEX_PASSWORD = "^(?=.*[\d])(?=.*[a-z])(?=.*[!@#$%^&*()])[\w\d!@#$%^&*()]{8,}$"
        if not re.fullmatch(REGEX_PASSWORD, password):
            raise ParseError(
                "비밀번호를 확인하세요. 최소 1개 이상의 소문자, 숫자, 특수문자로 구성되어야 하며 길이는 8자리 이상이어야 합니다."
            )

    @swagger_auto_schema(
        operation_summary="Sign up",
        responses={
            201: "Created",
            400: "bad request",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password", "team"],
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING, description="유저 id ( username )"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="유저 비밀번호"
                ),
                "team": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="유저가 속한 팀",
                    enum=Team.TeamChoices.values,
                ),
            },
        ),
    )
    def post(self, request):
        password = request.data.get("password")
        if not password:
            raise ParseError("password 가 입력되지 않았습니다.")

        team = request.data.get("team")
        if not team:
            raise ParseError("Team이 입력되지 않았습니다.")

        serializer = PrivateUserSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # self.validate_password(password)
                print(team)
                print(Team.objects.filter(name=team))
                user = serializer.save()
                user.team = get_object_or_404(Team, name=team)
                user.set_password(password)
                user.save()
                serializer = PrivateUserSerializer(user)
                login(request, user)

                return Response(
                    {"Succuess"},
                    status=201,
                )
        else:
            return Response(serializer.errors, status=400)


class LogOut(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Logout",
        operation_description="로그아웃",
        request_body=openapi.Schema(
            type="None",
            properties={},
        ),
        responses={200: "OK", 403: "Forbidden"},
    )
    def post(self, request):
        logout(request)
        return Response({"LogOut": True})
