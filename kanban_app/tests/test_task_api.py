from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User
from kanban_app.models import Board, Task


class TaskApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="taskuser@example.com",
            password="TestPassword123!",
            fullname="Task User",
        )
        self.board = Board.objects.create(
            title="Task Board",
            owner=self.user,
        )
        self.board.members.add(self.user)
        self.client.force_authenticate(user=self.user)

    def create_task(self):
        return Task.objects.create(
            board=self.board,
            created_by=self.user,
            title="Test Task",
            description="Test description",
            status="to-do",
            priority="high",
            assignee=self.user,
            reviewer=self.user,
            due_date="2026-08-20",
        )

    def test_create_task(self):
        data = {
            "board": self.board.id,
            "title": "New Task",
            "description": "Description",
            "status": "to-do",
            "priority": "high",
            "assignee_id": self.user.id,
            "reviewer_id": self.user.id,
            "due_date": "2026-08-20",
        }
        response = self.client.post("/api/tasks/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_task(self):
        task = self.create_task()
        response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {"status": "done"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "done")

    def test_board_cannot_be_changed(self):
        task = self.create_task()
        response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {"board": 999},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_same_board_can_be_sent_when_updating(self):
        task = self.create_task()
        response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {"board": self.board.id, "status": "done"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_task(self):
        task = self.create_task()
        response = self.client.delete(f"/api/tasks/{task.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_assigned_to_me(self):
        task = self.create_task()
        response = self.client.get("/api/tasks/assigned-to-me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], task.id)

    def test_reviewing(self):
        task = self.create_task()
        response = self.client.get("/api/tasks/reviewing/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], task.id)
