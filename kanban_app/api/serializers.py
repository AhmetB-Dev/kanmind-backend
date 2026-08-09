from rest_framework import serializers

from auth_app.models import User
from kanban_app.models import Board, Comment, Task


class BoardSerializer(serializers.ModelSerializer):
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
        members = validated_data.pop("members", [])
        board = Board.objects.create(
            owner=self.context["request"].user,
            **validated_data,
        )
        board.members.set(members)
        return board

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class TaskSummarySerializer(serializers.ModelSerializer):
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
    owner_id = serializers.IntegerField(read_only=True)
    members = UserSummarySerializer(many=True, read_only=True)
    tasks = TaskSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]


class BoardUpdateSerializer(serializers.ModelSerializer):
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
        self._validate_task_users(attrs["board"], attrs)
        return attrs

    def _has_board_access(self, board, user):
        return board.owner == user or board.members.filter(pk=user.pk).exists()

    def _validate_task_users(self, board, attrs):
        for field in ["assignee", "reviewer"]:
            user = attrs.get(field)
            if user and not self._has_board_access(board, user):
                raise serializers.ValidationError(
                    {field: "User must be a board member."}
                )

    def create(self, validated_data):
        return Task.objects.create(
            created_by=self.context["request"].user,
            **validated_data,
        )


class TaskUpdateSerializer(serializers.ModelSerializer):
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
        if "board" in self.initial_data:
            raise serializers.ValidationError(
                {"board": "Changing the board is not allowed."}
            )
        self._validate_users(attrs)
        return attrs

    def _validate_users(self, attrs):
        board = self.instance.board
        for field in ["assignee", "reviewer"]:
            user = attrs.get(field)
            if user and not self._has_access(board, user):
                raise serializers.ValidationError(
                    {field: "User must be a board member."}
                )

    def _has_access(self, board, user):
        return board.owner == user or board.members.filter(pk=user.pk).exists()


class TaskListSerializer(serializers.ModelSerializer):
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
