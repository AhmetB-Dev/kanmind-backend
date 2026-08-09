from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User
from kanban_app.models import Board, Comment, Task


class CommentApiTests(APITestCase):
    def setUp(self):
        self.user = self._create_user("comment@example.com", "Comment User")
        self.other_user = self._create_user("other@example.com", "Other User")
        self.board = self._create_board()
        self.task = self._create_task()
        self.client.force_authenticate(user=self.user)

    def test_create_comment(self):
        response = self.client.post(
            self._comments_url(),
            {"content": "Test comment"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], "Comment User")

    def test_get_comments(self):
        self._create_comment("Existing comment")
        response = self.client.get(self._comments_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_author_can_delete_comment(self):
        comment = self._create_comment("Delete me")
        response = self.client.delete(self._comment_url(comment))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_user_cannot_delete_comment(self):
        comment = self._create_comment("Protected comment")
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self._comment_url(comment))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_outsider_cannot_read_comments(self):
        outsider = self._create_user("outsider@example.com", "Outsider")
        self.client.force_authenticate(user=outsider)
        response = self.client.get(self._comments_url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _create_user(self, email, fullname):
        return User.objects.create_user(
            email=email,
            password="TestPassword123!",
            fullname=fullname,
        )

    def _create_board(self):
        board = Board.objects.create(title="Comment Board", owner=self.user)
        board.members.add(self.user, self.other_user)
        return board

    def _create_task(self):
        return Task.objects.create(
            board=self.board,
            created_by=self.user,
            title="Comment Task",
            status="to-do",
            priority="medium",
            due_date="2026-08-20",
        )

    def _create_comment(self, content):
        return Comment.objects.create(
            task=self.task,
            author=self.user,
            content=content,
        )

    def _comments_url(self):
        return f"/api/tasks/{self.task.id}/comments/"

    def _comment_url(self, comment):
        return f"{self._comments_url()}{comment.id}/"
