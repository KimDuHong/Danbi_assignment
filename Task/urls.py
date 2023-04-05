from django.urls import path
from . import views

urlpatterns = [
    path("", views.Tasks.as_view()),
    path("<int:pk>", views.TaskDetail.as_view()),
    path("subTask/<int:pk>", views.SubTasksDetail.as_view()),
    path("myTask", views.MyTasks.as_view()),
    path("myTask/main", views.MyMainTasks.as_view()),
    path("myTask/sub", views.MySubTasks.as_view()),
]
