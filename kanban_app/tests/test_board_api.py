"""Automated kanban API and permission tests."""

from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User
from kanban_app.models import Board


class BoardApiTests(APITestCase):
    """Verify boardapi behavior."""
    def setUp(self):
        self.user = User.objects.create_user(
            email="boarduser@example.com",
            password="TestPassword123!",
            fullname="Board User",
        )
        self.client.force_authenticate(user=self.user)

    def test_board_list(self):
        Board.objects.create(title="Board A", owner=self.user)

        response = self.client.get("/api/boards/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_board_create(self):
        data = {
            "title": "New Board",
            "members": [self.user.id],
        }

        response = self.client.post("/api/boards/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Board")
        self.assertEqual(response.data["owner_id"], self.user.id)

    def test_board_detail(self):
        board = Board.objects.create(title="Board A", owner=self.user)
        board.members.add(self.user)

        response = self.client.get(f"/api/boards/{board.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Board A")
        self.assertIn("members", response.data)
        self.assertIn("tasks", response.data)

    def test_board_update(self):
        board = Board.objects.create(title="Board A", owner=self.user)
        response = self.client.patch(
            f"/api/boards/{board.id}/",
            {"title": "Updated Board", "members": [self.user.id]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Board")
        self.assertEqual(response.data["owner_data"]["id"], self.user.id)

    def test_board_delete(self):
        board = Board.objects.create(title="Board A", owner=self.user)

        response = self.client.delete(f"/api/boards/{board.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Board.objects.filter(id=board.id).exists())
