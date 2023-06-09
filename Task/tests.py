from .models import Task, SubTask
from rest_framework.test import APITestCase
from User.models import User
from Team.models import Team

# path("", views.Tasks.as_view()),
# path("<int:pk>", views.TaskDetail.as_view()),
# path("subtask/<int:pk>", views.SubTasksDetail.as_view()),
# path("mytask", views.MyTasks.as_view()),
# path("mytask/main", views.MyMainTasks.as_view()),
# path("mytask/sub", views.MySubTasks.as_view()),

# /tasks/ GET POST
class TestTask(APITestCase):
    URL = "/api/v1/tasks/"

    @classmethod
    def setUpTestData(cls):
        print("")

        print("Test Task View & Create")
        cls.TITLE = "Task Test"
        cls.CONTENT = "Task Test"
        cls.upload_user = User.objects.create(username="Test User")
        for name in Team.TeamChoices.values:
            Team.objects.create(name=name)

    # def setUp(self):
    #     print("Test Task View & Create")
    #     self.TITLE = "Task Test"
    #     self.CONTENT = "Task Test"
    #     self.upload_user = User.objects.create(username="Test User")
    #     for name in Team.TeamChoices.values:
    #         Team.objects.create(name=name)

    # 비 로그인 유저가 조회
    def test_view_task_non_login_user(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 403, "비 로그인 조회")

    # 로그인 유저가 조회
    def test_view_task_logged_in_user(self):
        self.client.force_login(self.upload_user)
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200, "로그인 후 조회")

    # 비 로그인 유저가 생성
    def test_create_task_non_login_user(self):
        response = self.client.post(self.URL)
        self.assertEqual(response.status_code, 403, "비 로그인 업무 생성")

    def test_create_task_blank_value(self):
        self.client.force_login(self.upload_user)
        response = self.client.post(self.URL)
        self.assertEqual(response.status_code, 400, "post 공백 값")
        self.client.logout()

    def test_create_task_check_typo(self):
        self.client.force_login(self.upload_user)

        response = self.client.post(
            self.URL,
            data={
                "name": self.TITLE,
                "contentt": self.CONTENT,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400, "오타 확인")
        self.client.logout()

    def test_create_task_without_team(self):
        self.client.force_login(self.upload_user)

        response = self.client.post(
            self.URL,
            data={
                "title": self.TITLE,
                "content": self.CONTENT,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400, "팀 없이 post 하는 경우")
        self.client.logout()

    def test_create_task_non_existing_team_name(self):
        self.client.force_login(self.upload_user)

        response = self.client.post(
            self.URL,
            data={
                "title": self.TITLE,
                "content": self.CONTENT,
                "team": "No team",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 404, "존재하지 않는 팀명")
        self.client.logout()

    def test_create_task_with_existing_team_name(self):
        self.client.force_login(self.upload_user)

        response = self.client.post(
            self.URL,
            data={
                "title": self.TITLE,
                "content": self.CONTENT,
                "team": "단비",
            },
            format="json",
        )
        self.assertEqual(response.json().get("title"), self.TITLE, "정상 삽입 확인")
        self.assertEqual(
            response.json().get("create_user").get("username"),
            self.upload_user.username,
            "create user test",
        )
        self.assertEqual(response.status_code, 200, "정상 삽입")
        self.client.logout()

    def test_create_task_with_diff_type_of_subtasks(self):
        self.client.force_login(self.upload_user)

        response = self.client.post(
            self.URL,
            data={
                "title": self.TITLE,
                "content": self.CONTENT,
                "team": "단비",
                "subtasks": "단비",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400, "subtasks 의 자료형이 array 가 아닐때")
        self.client.logout()

    def test_create_task_with_wrong_value_of_subtasks(self):
        self.client.force_login(self.upload_user)

        response = self.client.post(
            self.URL,
            data={
                "title": self.TITLE,
                "content": self.CONTENT,
                "team": "단비",
                "subtasks": ["단비", "없는 팀"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 404, "array 의 중간에 이상한 값이 들어올 때")
        self.client.logout()

    def test_create_task_with_corret_case_team_and_subtasks(self):
        self.client.force_login(self.upload_user)

        response = self.client.post(
            self.URL,
            data={
                "title": self.TITLE,
                "content": self.CONTENT,
                "team": "단비",
                "subtasks": ["단비", "블라블라"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, "정상적인 경우")
        self.client.logout()

    def test_create_task_with_corret_case_subtasks_without_team(self):
        self.client.force_login(self.upload_user)

        response = self.client.post(
            self.URL,
            data={
                "title": self.TITLE,
                "content": self.CONTENT,
                "subtasks": ["단비", "블라블라"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, "정상적인 경우")
        self.client.logout()

    # /tasks/{id} GET PUT


# /tasks/{id} GET PUT
class TestTaskDetail(APITestCase):
    URL = "/api/v1/tasks"

    @classmethod
    def setUpTestData(cls):
        print("")

        print("Test Task Detail View & Edit")
        for name in Team.TeamChoices.values:
            Team.objects.create(name=name)
        cls.upload_user = User.objects.create(username="Test User")
        cls.team = Team.objects.get(name="단비")
        cls.task = Task.objects.create(
            title="Test Task",
            content="Test Task Content",
            create_user=cls.upload_user,
            team=cls.team,
        )
        cls.subtask = SubTask.objects.create(task=cls.task, team=cls.team)

    # 비 로그인 유저가 조회
    def test_view_task_detail_non_login_user(self):
        response = self.client.get(f"{self.URL}/{self.task.id}")
        self.assertEqual(response.status_code, 403, "비 로그인 조회")

    # 로그인 유저가 조회
    def test_view_task_detail_login_user(self):
        self.client.force_login(self.upload_user)
        response = self.client.get(f"{self.URL}/{self.task.id}")
        self.assertEqual(response.status_code, 200, "로그인 후 조회")
        self.client.logout()

    # 서브 업무 값 포함 여부 확인
    def test_view_task_detail_subtasks_value(self):
        self.client.force_login(self.upload_user)
        response = self.client.get(f"{self.URL}/{self.task.id}")
        self.assertEqual(
            response.json().get("id"),
            self.subtask.task.id,
            "서브 업무까지 재대로 보이는지 확인",
        )
        self.assertEqual(
            response.json().get("is_complete"),
            self.subtask.is_complete,
            "서브업무 완료 여부 확인",
        )
        self.client.logout()

    # 존재하지 않는 url 접근
    def test_view_task_detail_not_found_url(self):
        self.client.force_login(self.upload_user)
        response = self.client.get(f"{self.URL}/10")
        self.assertEqual(response.status_code, 404, "존재하지 않는 url")
        self.client.logout()

    # 비 로그인 유저가 수정
    def test_edit_task_detail_non_login_user(self):
        response = self.client.put(
            f"{self.URL}/{self.task.id}",
            data={"title": "Change test"},
            format="json",
        )
        self.assertEqual(response.status_code, 403, "비 로그인 수정")

    # 생성한 유저가 아닌 유저가 수정
    def test_edit_task_detail_not_create_user(self):
        user = User.objects.create(username="OtherUser")
        self.client.force_login(user)
        response = self.client.put(
            f"{self.URL}/{self.task.id}",
            data={"title": "Change test"},
            format="json",
        )
        self.assertEqual(response.status_code, 403, "로그인 (업로드 유저가 아닌 유저) 후 수정")
        self.client.logout()

    # 생성한 유저가 수정
    def test_edit_task_detail_create_user(self):
        self.client.force_login(self.upload_user)

        response = self.client.put(
            f"{self.URL}/{self.task.id}",
            data={"title": "Change test"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, "로그인 (업로드 유저) 후 수정")
        self.client.logout()

    # 정상적 수정 확인
    def test_edit_task_detail_create_user_change_value(self):
        self.client.force_login(self.upload_user)
        response = self.client.put(
            f"{self.URL}/{self.task.id}",
            data={"title": "Change test"},
            format="json",
        )
        self.assertEqual(
            Task.objects.get(pk=self.task.pk).title,
            "Change test",
            "수정 여부 확인",
        )
        self.client.logout()

    # 존재하지 않는 팀 이름 입력
    def test_edit_task_detail_non_existing_team_name(self):
        self.client.force_login(self.upload_user)

        response = self.client.put(
            f"{self.URL}/{self.task.id}",
            data={"team": "없는 팀"},
            format="json",
        )
        self.assertEqual(response.status_code, 404, "없는 팀 이름 입력")
        self.client.logout()

    # 정상적인 팀 이름 입력
    def test_edit_task_detail_correct_team_name(self):
        self.client.force_login(self.upload_user)

        response = self.client.put(
            f"{self.URL}/{self.task.id}",
            data={"team": "단비"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, "정상적 요청")
        self.client.logout()

    # 존재하지 않는 url 접근
    def test_edit_task_detail_non_existing_url(self):
        self.client.force_login(self.upload_user)

        response = self.client.put(f"{self.URL}/10")
        self.assertEqual(response.status_code, 404, "존재하지 않는 url")

        self.client.logout()

    # subtasks 의 자료형이 array 가 아닌 경우
    def test_edit_task_detail_diff_type_subtasks(self):
        self.client.force_login(self.upload_user)

        response = self.client.put(
            f"{self.URL}/{self.task.id}",
            data={
                "subtasks": "단비",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400, "subtasks 의 자료형이 array 가 아닐때")
        self.client.logout()

    # 존재하지 않는 팀 이름이 입력딜때
    def test_edit_task_detail_non_existing_name_subtasks_team(self):
        self.client.force_login(self.upload_user)

        response = self.client.put(
            f"{self.URL}/{self.task.id}",
            data={
                "subtasks": ["단비", "없는 팀"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 404, "array 의 중간에 이상한 값이 들어올 때")

        self.client.logout()

    # 정상적인 경우
    def test_edit_task_detail_correct_name_subtasks_team(self):
        self.client.force_login(self.upload_user)

        response = self.client.put(
            f"{self.URL}/{self.task.id}",
            data={
                "subtasks": ["단비", "블라블라"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, "정상적인 경우")

        self.client.logout()

    # 완료된 작업은 삭제 되지 않아야함
    def test_edit_task_detail_delete_except_completed_subtasks_team(self):
        self.client.force_login(self.upload_user)

        subtask = Task.objects.get(pk=self.task.pk).subtasks.filter()[0]
        subtask.is_complete = True
        subtask.save()

        response = self.client.put(
            f"{self.URL}/{self.task.id}",
            data={
                "subtasks": ["수피", "철로"],
            },
            format="json",
        )
        self.assertEqual(
            Task.objects.get(pk=self.task.pk).subtasks.all().count(),
            3,
            "완료된 작업 삭제 여부 확인",
        )

        self.client.logout()

    # 서브 작업 완료시 자동 완료
    def test_edit_task_detail_auto_complete_all_subtasks_done(self):
        self.client.force_login(self.upload_user)

        self.assertEqual(
            Task.objects.get(pk=self.task.pk).is_complete,
            False,
            "서브 작업 완료시 자동 완료 여부 확인",
        )
        self.assertEqual(
            Task.objects.get(pk=self.task.pk).completed_date,
            None,
            "서브 작업 완료시 자동 갱신",
        )
        # 모든 subtask를 완료 상태로 변경
        for i in Task.objects.get(pk=self.task.pk).subtasks.all():
            i.is_complete = True
            i.save()

        self.assertEqual(
            Task.objects.get(pk=self.task.pk).is_complete,
            True,
            "서브 작업 완료시 자동 완료 여부 확인",
        )

        self.assertEqual(
            bool(Task.objects.get(pk=self.task.pk).completed_date),
            True,
            "서브 작업 완료시 자동 갱신",
        )

        self.client.logout()

    # 작업중인 팀이 아무도 없을 때
    def test_edit_task_detail_non_existing_any_team(self):
        self.client.force_login(self.upload_user)

        task = Task.objects.create(
            title="Test Task2",
            content="Test Task Content2",
            create_user=self.upload_user,
        )
        subtask = SubTask.objects.create(task=task, team=self.team)
        response = self.client.put(
            f"{self.URL}/{task.id}",
            data={
                "subtasks": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400, "수정 후 아무런 팀도 없는 경우")

        self.client.logout()


# /tasks/subtask/{id} GET PUT
class TestSubTaskDetail(APITestCase):

    URL = "/api/v1/tasks/subtask"

    # 기본 데이터들
    @classmethod
    def setUpTestData(cls):
        print("")
        print("Test SubTask Detail View & Edit")
        for name in Team.TeamChoices.values:
            Team.objects.create(name=name)
        cls.team = Team.objects.get(name="단비")
        cls.upload_user = User.objects.create(username="Test User", team=cls.team)
        cls.task = Task.objects.create(
            title="Test Task",
            content="Test Task Content",
            create_user=cls.upload_user,
            team=cls.team,
        )
        cls.subtask = SubTask.objects.create(task=cls.task, team=cls.team)

    # 비 로그인 유저가 조회
    def test_view_subtask_detail_unauthenticated(self):

        response = self.client.get(f"{self.URL}/{self.subtask.id}")
        self.assertEqual(
            response.status_code, 403, "Unauthenticated user cannot view subtask"
        )

    # 로그인 유저가 조회
    def test_view_subtask_detail_authenticated(self):

        self.client.force_login(self.upload_user)

        response = self.client.get(f"{self.URL}/{self.subtask.id}")
        self.assertEqual(
            response.status_code, 200, "Authenticated user can view subtask"
        )
        self.assertEqual(
            response.json().get("pk"),
            self.subtask.id,
            "Wrong value",
        )
        self.assertEqual(
            response.json().get("is_complete"),
            self.subtask.is_complete,
            "Wrong value",
        )

        self.client.logout()

    # 존재하지 않는 url 접근
    def test_view_subtask_detail_nonexistent_id(self):
        self.client.force_login(self.upload_user)
        response = self.client.get(f"{self.URL}/10")
        self.assertEqual(response.status_code, 404, "존재하지 않는 url")

    def test_edit_subtask_detail_unauthenticated(self):
        response = self.client.put(
            f"{self.URL}/{self.subtask.id}",
            data={"is_complete": "true"},
            format="json",
        )
        self.assertEqual(
            response.status_code, 403, "Unauthenticated user cannot edit subtask"
        )

        self.client.logout()

    def test_edit_subtask_detail_wrong_user(self):
        user = User.objects.create(username="OtherUser")
        self.client.force_login(user)

        response = self.client.put(
            f"{self.URL}/{self.subtask.id}",
            data={"title": "Change test"},
            format="json",
        )
        self.assertEqual(response.status_code, 403, "Wrong user cannot edit subtask")

        self.client.logout()

    def test_edit_subtask_detail_authenticated(self):

        self.client.force_login(self.upload_user)
        response = self.client.put(
            f"{self.URL}/{self.subtask.id}",
            data={"is_complete": "true"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, "로그인 (업로드 유저) 후 수정")

        self.client.logout()

    def test_edit_subtask_detail_authenticated_complete(self):
        self.client.force_login(self.upload_user)
        self.assertEqual(
            SubTask.objects.get(pk=self.subtask.pk).task.is_complete,
            False,
            "완료 전",
        )
        self.client.put(
            f"{self.URL}/{self.subtask.id}",
            data={"is_complete": "true"},
            format="json",
        )

        self.assertEqual(
            SubTask.objects.get(pk=self.subtask.pk).is_complete,
            True,
            "수정 여부 확인",
        )
        self.assertEqual(
            SubTask.objects.get(pk=self.subtask.pk).task.is_complete,
            True,
            "완료 후",
        )

        self.client.logout()

    def test_edit_subtask_detail_authenticated_complete_date(self):
        self.client.force_login(self.upload_user)
        self.assertEqual(
            SubTask.objects.get(pk=self.subtask.pk).task.completed_date,
            None,
            "완료 전 날짜",
        )
        self.client.put(
            f"{self.URL}/{self.subtask.id}",
            data={"is_complete": "true"},
            format="json",
        )
        self.assertEqual(
            bool(SubTask.objects.get(pk=self.subtask.pk).task.completed_date),
            True,
            "완료 후 날짜",
        )

        self.client.logout()


# /tasks/mytask GET
class TestViewMyTasks(APITestCase):

    URL = "/api/v1/tasks/mytask"

    @classmethod
    def setUpTestData(self):
        # first_tasK => 내 팀이 task 에만 속하는 경우
        # second_tasK => 내 팀이 속하지 않은 업무
        # third_tasK => 내 팀이 subtask 에 속하는 경우\
        print("")

        print("Test MyTask View")
        for name in Team.TeamChoices.values:
            Team.objects.create(name=name)
        self.first_team = Team.objects.get(name="단비")
        self.second_team = Team.objects.get(name="블라블라")
        self.first_user = User.objects.create(
            username="Test User", team=self.first_team
        )
        self.second_user = User.objects.create(
            username="Test User2", team=self.second_team
        )
        self.first_task = Task.objects.create(
            title="First Task",
            content="Test Task Content",
            create_user=self.first_user,
            team=self.first_team,
        )
        self.second_task = Task.objects.create(
            title="Second Task",
            content="Test Task Content",
            create_user=self.second_user,
            team=self.second_team,
        )
        self.third_task = Task.objects.create(
            title="First Task",
            content="Test Task Content",
            create_user=self.second_user,
            team=self.second_team,
        )
        self.first_subtask = SubTask.objects.create(
            task=self.first_task, team=self.first_team
        )
        self.first_subtask = SubTask.objects.create(
            task=self.second_task, team=self.second_team
        )
        self.first_subtask = SubTask.objects.create(
            task=self.third_task, team=self.first_team
        )

    def test_view_my_task_non_login_user(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 403, "비 로그인 조회")

    def test_view_my_task_login_user(self):
        self.client.force_login(self.first_user)

        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200, "로그인 조회")

        self.client.logout()

    def test_view_my_tasks_value_is_correct(self):
        self.client.force_login(self.first_user)

        response = self.client.get(self.URL)

        self.assertEqual(len(response.json()), 2, "메인 업무 1개, 서브 업무 1개")
        self.assertEqual(response.json()[0].get("id"), 1, "first task")
        self.assertEqual(response.json()[1].get("id"), 3, "thrid task")

        self.client.logout()

    def test_view_my_tasks_value_is_correct_other_user(self):
        self.client.force_login(self.second_user)

        response = self.client.get(self.URL)

        self.assertEqual(len(response.json()), 2, "메인 업무 2개")
        self.assertEqual(response.json()[0].get("id"), 2, "second task")
        self.assertEqual(response.json()[1].get("id"), 3, "thrid task")

        self.client.logout()


# /tasks/mytask/main GET
class TestViewMyMainTasks(APITestCase):

    URL = "/api/v1/tasks/mytask/main"

    @classmethod
    def setUpTestData(self):
        # first_tasK => 내 팀이 task 에만 속하는 경우
        # second_tasK => 내 팀이 속하지 않은 업무
        # third_tasK => 내 팀이 subtask 에 속하는 경우
        print("")

        print("Test MyMainTask View")
        for name in Team.TeamChoices.values:
            Team.objects.create(name=name)
        self.first_team = Team.objects.get(name="단비")
        self.second_team = Team.objects.get(name="블라블라")
        self.first_user = User.objects.create(
            username="Test User", team=self.first_team
        )
        self.second_user = User.objects.create(
            username="Test User2", team=self.second_team
        )
        self.first_task = Task.objects.create(
            title="First Task",
            content="Test Task Content",
            create_user=self.first_user,
            team=self.first_team,
        )
        self.second_task = Task.objects.create(
            title="Second Task",
            content="Test Task Content",
            create_user=self.second_user,
            team=self.second_team,
        )
        self.third_task = Task.objects.create(
            title="First Task",
            content="Test Task Content",
            create_user=self.second_user,
            team=self.second_team,
        )
        self.first_subtask = SubTask.objects.create(
            task=self.first_task, team=self.first_team
        )
        self.first_subtask = SubTask.objects.create(
            task=self.second_task, team=self.second_team
        )
        self.first_subtask = SubTask.objects.create(
            task=self.third_task, team=self.first_team
        )

    def test_view_my_main_task_non_login_user(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 403, "비 로그인 조회")

    def test_view_my_main_task_login_user(self):
        self.client.force_login(self.first_user)

        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200, "로그인 조회")

        self.client.logout()

    def test_view_my_main_task_is_correct_value(self):
        self.client.force_login(self.first_user)

        response = self.client.get(self.URL)

        self.assertEqual(len(response.json()), 1, "메인 업무 1개")
        self.assertEqual(response.json()[0].get("id"), 1, "first task")

        self.client.logout()

    def test_view_my_main_task_is_correct_value_other_user(self):
        self.client.force_login(self.second_user)

        response = self.client.get(self.URL)

        self.assertEqual(response.json()[0].get("id"), 2, "second task")
        self.assertEqual(response.json()[1].get("id"), 3, "thrid task")

        self.client.logout()


# tasks/mytask/sub GET
class TestViewMySubTasks(APITestCase):

    URL = "/api/v1/tasks/mytask/sub"

    @classmethod
    def setUpTestData(self):
        # first_tasK => 내 팀이 task 에만 속하는 경우
        # second_tasK => 내 팀이 속하지 않은 업무
        # third_tasK => 내 팀이 subtask 에 속하는 경우
        print("")

        print("Test MySubTask View")
        for name in Team.TeamChoices.values:
            Team.objects.create(name=name)
        self.first_team = Team.objects.get(name="단비")
        self.second_team = Team.objects.get(name="블라블라")
        self.first_user = User.objects.create(
            username="Test User", team=self.first_team
        )
        self.second_user = User.objects.create(
            username="Test User2", team=self.second_team
        )
        self.first_task = Task.objects.create(
            title="First Task",
            content="Test Task Content",
            create_user=self.first_user,
            team=self.first_team,
        )
        self.second_task = Task.objects.create(
            title="Second Task",
            content="Test Task Content",
            create_user=self.second_user,
            team=self.second_team,
        )
        self.third_task = Task.objects.create(
            title="First Task",
            content="Test Task Content",
            create_user=self.second_user,
            team=self.second_team,
        )
        self.first_subtask = SubTask.objects.create(
            task=self.first_task, team=self.first_team
        )
        self.first_subtask = SubTask.objects.create(
            task=self.second_task, team=self.second_team
        )
        self.first_subtask = SubTask.objects.create(
            task=self.third_task, team=self.first_team
        )

    def test_view_my_sub_task_non_login_user(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 403, "비 로그인 조회")

    def test_view_my_sub_task_login_user(self):
        self.client.force_login(self.first_user)

        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200, "로그인 조회")

        self.client.logout()

    def test_view_my_sub_task_is_correct_value(self):
        self.client.force_login(self.first_user)

        response = self.client.get(self.URL)

        self.assertEqual(len(response.json()), 2, "서브 업무 2개")
        self.assertEqual(response.json()[0].get("id"), 1, "first task")
        self.assertEqual(response.json()[1].get("id"), 3, "thrid task")

        self.client.logout()

    def test_view_my_sub_Task_is_correct_value_other_user(self):
        self.client.force_login(self.second_user)

        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200, "로그인 조회")
        self.assertEqual(len(response.json()), 1, "서브 업무 1개")
        self.assertEqual(response.json()[0].get("id"), 2, "second task")

        self.client.logout()
