# KanMind Backend

KanMind Backend is a REST API for a kanban-style task management application.  
It provides authentication, board management, task workflows, member assignment, reviews, comments, and permission-based access control.

The backend is built with **Django** and **Django REST Framework** and is designed to work with the separate KanMind frontend.

## Quick Start

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd kanmind-backend
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Optional: create the demo guest user

```bash
python manage.py create_guest_user
```

### 6. Start the development server

```bash
python manage.py runserver
```

The API is then available at:

```text
http://127.0.0.1:8000/api/
```

The Django admin is available at:

```text
http://127.0.0.1:8000/admin/
```

## Features

- User registration and login
- Token-based authentication
- Email lookup for existing users
- Create, read, update, and delete boards
- Board ownership and member management
- Create, update, assign, review, and delete tasks
- Task status workflow:
  - `to-do`
  - `in-progress`
  - `review`
  - `done`
- Task priorities:
  - `low`
  - `medium`
  - `high`
- Assigned-to-me task view
- Reviewing task view
- Task comments
- Permission-based access control
- Django admin interface
- Automated API and permission tests
- Optional guest/demo user

## Tech Stack

- Python
- Django 6.0.7
- Django REST Framework 3.17.1
- django-cors-headers 4.9.0
- Django REST Framework Token Authentication
- SQLite
- Coverage.py

## Frontend Connection

The local development configuration allows requests from:

```text
http://127.0.0.1:5500
```

This is configured through `django-cors-headers`.

## Authentication

The API uses Django REST Framework token authentication.

After registration or login, the API returns a token. Authenticated requests must send it in the request header:

```http
Authorization: Token <your-token>
```

Registration and login are public endpoints. All other application endpoints require authentication.

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/registration/` | Register a new user |
| `POST` | `/api/login/` | Log in and receive an authentication token |
| `GET` | `/api/email-check/?email=<email>` | Find a registered user by email |

### Boards

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/boards/` | List boards owned by or shared with the current user |
| `POST` | `/api/boards/` | Create a new board |
| `GET` | `/api/boards/{board_id}/` | Get board details including members and tasks |
| `PATCH` | `/api/boards/{board_id}/` | Update board title or members |
| `DELETE` | `/api/boards/{board_id}/` | Delete a board |

### Tasks

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/tasks/` | Create a task |
| `PATCH` | `/api/tasks/{task_id}/` | Update a task |
| `DELETE` | `/api/tasks/{task_id}/` | Delete a task |
| `GET` | `/api/tasks/assigned-to-me/` | List tasks assigned to the current user |
| `GET` | `/api/tasks/reviewing/` | List tasks the current user is reviewing |

### Comments

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/tasks/{task_id}/comments/` | List comments for a task |
| `POST` | `/api/tasks/{task_id}/comments/` | Add a comment to a task |
| `DELETE` | `/api/tasks/{task_id}/comments/{comment_id}/` | Delete a comment |

## Permissions

KanMind uses object-level permissions to protect boards, tasks, and comments.

- A board owner or board member can access and edit the board.
- Only the board owner can delete the board.
- A board owner or member can create and update tasks on that board.
- Assignees and reviewers must belong to the board or be its owner.
- A task can only be deleted by its creator or the board owner.
- A board owner or member can read and create task comments.
- Only the comment author can delete their own comment.
- Users without the required board access receive `403 Forbidden`.

## Example: Create a Board

```json
{
  "title": "Project Board",
  "members": [2, 3]
}
```

The authenticated user automatically becomes the board owner.

## Example: Create a Task

```json
{
  "board": 1,
  "title": "Implement authentication",
  "description": "Add token-based login and registration.",
  "status": "to-do",
  "priority": "high",
  "assignee_id": 2,
  "reviewer_id": 3,
  "due_date": "2026-08-20"
}
```

`assignee_id` and `reviewer_id` may also be `null`.

## Testing

Run the complete Django test suite with:

```bash
python manage.py test
```

Current project status:

```text
40 tests
All tests passing
99% test coverage
```

Measure coverage with:

```bash
python -m coverage run manage.py test
python -m coverage report
```

An optional HTML coverage report can be generated with:

```bash
python -m coverage html
```

The generated `.coverage` file and `htmlcov/` directory are excluded from Git.

## Development Notes

- The project uses a custom user model with email as the login identifier.
- Board, task, and comment permissions are handled through dedicated DRF permission classes.
- API validation and response transformation are handled by serializers.
- The database is intentionally excluded from version control.
- The frontend and backend are maintained separately.
- `PUT` is intentionally disabled for boards; board updates use `PATCH`.
- A task cannot be moved to another board through the task update endpoint.

## Security Note

The included Django configuration is intended for local development. Before a production deployment, environment-specific values such as the Django secret key, debug mode, allowed hosts, CORS origins, and database configuration should be moved to secure production settings or environment variables.
