from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User
from kanban_app.models import Board, Task


class TaskPermissionTests(APITestCase):
    def setUp(self):
        self.owner = self._create_user("owner@example.com")
        self.member = self._create_user("member@example.com")
        self.outsider = self._create_user("outsider@example.com")
        self.board = Board.objects.create(title="Board", owner=self.owner)
        self.board.members.add(self.member)

    def _create_user(self, email):
        return User.objects.create_user(
            email=email,
            password="TestPassword123!",
            fullname="Test User",
        )

    def _create_task(self):
        return Task.objects.create(
            board=self.board,
            created_by=self.owner,
            title="Permission Task",
            status="to-do",
            priority="medium",
            due_date="2026-08-20",
        )

    def test_create_requires_authentication(self):
        response = self.client.post("/api/tasks/", {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_outsider_cannot_create_task(self):
        self.client.force_authenticate(user=self.outsider)
        data = self._task_data()
        response = self.client.post("/api/tasks/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_outsider_cannot_update_task(self):
        task = self._create_task()
        self.client.force_authenticate(user=self.outsider)
        response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {"title": "Forbidden"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_update_task(self):
        task = self._create_task()
        self.client.force_authenticate(user=self.member)
        response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {"title": "Allowed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_member_cannot_delete_foreign_task(self):
        task = self._create_task()
        self.client.force_authenticate(user=self.member)
        response = self.client.delete(f"/api/tasks/{task.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_assignee_is_rejected(self):
        self.client.force_authenticate(user=self.owner)
        data = self._task_data()
        data["assignee_id"] = self.outsider.id
        response = self.client.post("/api/tasks/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _task_data(self):
        return {
            "board": self.board.id,
            "title": "New Task",
            "description": "Test",
            "status": "to-do",
            "priority": "medium",
            "due_date": "2026-08-20",
        }
