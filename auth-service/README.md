# Auth Service — Techno Zone

Handles user registration, login, JWT issuance, and token verification.

**Port:** `3001`  
**Base URL:** `/api/auth`

## Endpoints

| Method | Path            | Auth | Description                        |
|--------|-----------------|------|------------------------------------|
| POST   | /register       | —    | Create account → returns JWT       |
| POST   | /login          | —    | Login → returns JWT                |
| GET    | /me             | JWT  | Get current user profile           |
| POST   | /verify         | JWT  | Validate token (used by Gateway)   |
| POST   | /logout         | —    | Client-side logout instruction     |

## Request / Response Examples

### POST /api/auth/register
```json
// Request
{ "name": "Ahmed", "email": "ahmed@example.com", "password": "secret123" }

// Response 201
{
  "success": true,
  "data": {
    "user": { "id": 1, "name": "Ahmed", "email": "ahmed@example.com" },
    "token": "<jwt>"
  }
}
```

### POST /api/auth/login
```json
// Request
{ "email": "ahmed@example.com", "password": "secret123" }

// Response 200
{ "success": true, "data": { "user": {...}, "token": "<jwt>" } }
```

### GET /api/auth/me
```
Authorization: Bearer <jwt>
```

## Setup

```bash
cp .env.example .env        # Fill in your values
pip install -r requirements.txt
python app.py               # Dev server on :3001
```

## Docker

```bash
docker build -t auth-service .
docker run -p 3001:3001 --env-file .env auth-service
```

## JWT Usage by Other Services

Include in every protected request:
```
Authorization: Bearer <token>
```
Other services can call `POST /api/auth/verify` (via API Gateway) to validate tokens, or use the shared `utils/jwt_utils.py` `decode_token()` directly.
