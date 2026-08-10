"""Serializers for KanMind boards, tasks, users, and comments."""

from rest_framework import serializers

from auth_app.models import User
from kanban_app.models import Board, Comment, Task


class BoardSerializer(serializers.ModelSerializer):
    """Serialize board lists and board creation data."""

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "members",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]

    def create(self, validated_data):
        """Create a board owned by the authenticated user."""
        members = validated_data.pop("members", [])
        board = Board.objects.create(
            owner=self.context["request"].user,
            **validated_data,
        )
        board.members.set(members)
        return board

    def get_member_count(self, obj):
        """Return the number of users assigned as board members."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return the total number of tasks on the board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Return the number of tasks in the to-do state."""
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of high-priority tasks."""
        return obj.tasks.filter(priority="high").count()


class UserSummarySerializer(serializers.ModelSerializer):
    """Expose compact user data inside board and task responses."""

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class TaskSummarySerializer(serializers.ModelSerializer):
    """Serialize tasks embedded in board detail responses."""

    assignee = UserSummarySerializer(read_only=True)
    reviewer = UserSummarySerializer(read_only=True)
    comments_count = serializers.IntegerField(
        source="comments.count",
        read_only=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]


class BoardDetailSerializer(serializers.ModelSerializer):
    """Serialize a board together with members and tasks."""

    owner_id = serializers.IntegerField(read_only=True)
    members = UserSummarySerializer(many=True, read_only=True)
    tasks = TaskSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Handle board updates and return expanded owner/member data."""

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
        write_only=True,
    )
    owner_data = UserSummarySerializer(source="owner", read_only=True)
    members_data = UserSummarySerializer(
        source="members",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "members",
            "owner_data",
            "members_data",
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    """Validate and create tasks for an accessible board."""

    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer",
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )
    assignee = UserSummarySerializer(read_only=True)
    reviewer = UserSummarySerializer(read_only=True)
    comments_count = serializers.IntegerField(
        source="comments.count",
        read_only=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def validate(self, attrs):
        """Validate assignee and reviewer access to the selected board."""
        self._validate_task_users(attrs["board"], attrs)
        return attrs

    def _has_board_access(self, board, user):
        """Return whether a user owns or belongs to the board."""
        is_owner = board.owner == user
        is_member = board.members.filter(pk=user.pk).exists()
        return is_owner or is_member

    def _validate_task_users(self, board, attrs):
        """Reject assignees or reviewers without access to the board."""
        for field in ["assignee", "reviewer"]:
            user = attrs.get(field)
            if user and not self._has_board_access(board, user):
                raise serializers.ValidationError(
                    {field: "User must be a board member."}
                )

    def create(self, validated_data):
        """Create a task and record the authenticated user as its creator."""
        return Task.objects.create(
            created_by=self.context["request"].user,
            **validated_data,
        )


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Validate partial task updates without allowing board changes."""

    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer",
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )
    assignee = UserSummarySerializer(read_only=True)
    reviewer = UserSummarySerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "assignee",
            "reviewer",
            "due_date",
        ]

    def validate(self, attrs):
        """Validate board immutability and task user assignments."""
        self._validate_board()
        self._validate_users(attrs)
        return attrs

    def _validate_board(self):
        """Allow the current board ID but reject moving the task."""
        board_id = self.initial_data.get("board")
        if board_id is None:
            return
        if str(board_id) != str(self.instance.board_id):
            raise serializers.ValidationError(
                {"board": "Changing the board is not allowed."}
            )

    def _validate_users(self, attrs):
        """Reject updated assignees or reviewers without board access."""
        board = self.instance.board
        for field in ["assignee", "reviewer"]:
            user = attrs.get(field)
            if user and not self._has_access(board, user):
                raise serializers.ValidationError(
                    {field: "User must be a board member."}
                )

    def _has_access(self, board, user):
        """Return whether a user owns or belongs to the board."""
        is_owner = board.owner == user
        is_member = board.members.filter(pk=user.pk).exists()
        return is_owner or is_member


class TaskListSerializer(serializers.ModelSerializer):
    """Serialize task lists for assignment and review endpoints."""

    assignee = UserSummarySerializer(read_only=True)
    reviewer = UserSummarySerializer(read_only=True)
    comments_count = serializers.IntegerField(
        source="comments.count",
        read_only=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Serialize task comments with the author's display name."""

    author = serializers.CharField(
        source="author.fullname",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "created_at",
            "author",
            "content",
        ]
        read_only_fields = ["id", "created_at", "author"]
