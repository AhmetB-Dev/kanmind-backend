from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User
from kanban_app.models import Board


class BoardPermissionTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="TestPassword123!",
            fullname="Owner User",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="TestPassword123!",
            fullname="Other User",
        )
        self.board = Board.objects.create(
            title="Private Board",
            owner=self.owner,
        )

    def test_board_list_requires_authentication(self):
        response = self.client.get("/api/boards/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_member_cannot_view_board(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f"/api/boards/{self.board.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_member_cannot_update_board(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(
            f"/api/boards/{self.board.id}/",
            {"title": "Not Allowed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_owner_cannot_delete_board(self):
        self.board.members.add(self.other_user)
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(f"/api/boards/{self.board.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
