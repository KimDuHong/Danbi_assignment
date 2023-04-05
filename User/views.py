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


class Login(APIView):
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
                    {"Signup": "Succuess"},
                    status=201,
                )
        else:
            return Response(serializer.errors, status=400)


class LogOut(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="로그아웃 api",
        operation_description="로그아웃",
        responses={200: "OK", 403: "Forbidden"},
    )
    def post(self, request):
        logout(request)
        return Response({"LogOut": True})
