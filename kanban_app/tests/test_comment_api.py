from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User
from kanban_app.models import Board, Comment, Task


class CommentApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="comment@example.com",
            password="TestPassword123!",
            fullname="Comment User",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="TestPassword123!",
            fullname="Other User",
        )
        self.board = Board.objects.create(
            title="Comment Board",
            owner=self.user,
        )
        self.board.members.add(self.other_user)
        self.task = Task.objects.create(
            board=self.board,
            created_by=self.user,
            title="Comment Task",
            status="to-do",
            priority="medium",
            due_date="2026-08-20",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_comment(self):
        response = self.client.post(
            f"/api/tasks/{self.task.id}/comments/",
            {"content": "Test comment"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], "Comment User")

    def test_get_comments(self):
        Comment.objects.create(
            task=self.task,
            author=self.user,
            content="Existing comment",
        )

        response = self.client.get(f"/api/tasks/{self.task.id}/comments/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_author_can_delete_comment(self):
        comment = Comment.objects.create(
            task=self.task,
            author=self.user,
            content="Delete me",
        )

        response = self.client.delete(
            f"/api/tasks/{self.task.id}/comments/{comment.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_user_cannot_delete_comment(self):
        comment = Comment.objects.create(
            task=self.task,
            author=self.user,
            content="Protected comment",
        )
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(
            f"/api/tasks/{self.task.id}/comments/{comment.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_outsider_cannot_read_comments(self):
        outsider = User.objects.create_user(
            email="outsider@example.com",
            password="TestPassword123!",
            fullname="Outsider",
        )
        self.client.force_authenticate(user=outsider)

        response = self.client.get(f"/api/tasks/{self.task.id}/comments/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
