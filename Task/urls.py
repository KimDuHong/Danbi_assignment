from django.urls import path
from . import views

urlpatterns = [
    path("", views.Tasks.as_view()),
    path("<int:pk>", views.TaskDetail.as_view()),
    path("subtask/<int:pk>", views.SubTasksDetail.as_view()),
    path("mytask", views.MyTasks.as_view()),
    path("mytask/main", views.MyMainTasks.as_view()),
    path("mytask/sub", views.MySubTasks.as_view()),
]
