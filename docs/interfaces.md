# API Interface Documentation
# test
## Base URL
`http://localhost:8000/api/v1`

## Authentication
All endpoints except `/auth/login` require a Bearer token in the `Authorization` header.

## Endpoints

### POST /auth/login
Authenticate user and return JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "token": "string",
  "expires_in": 3600
}
```

### GET /users/{id}
Retrieve user profile by ID.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": "integer",
  "username": "string",
  "email": "string",
  "created_at": "datetime"
}
```

### POST /users
Create a new user.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response (201):**
```json
{
  "id": "integer",
  "username": "string",
  "email": "string"
}
```

### Error Responses
All errors return a standard format:
```json
{
  "error": "string",
  "message": "string",
  "status_code": "integer"
}
```
