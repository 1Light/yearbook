### Endpoint: **POST** `/api/login/`

* **Description**: Authenticates a user and returns JWT tokens along with user info.
* **Request Body** (JSON):

  ```json
  {
    "email": "user@example.com",
    "password": "userpassword"
  }
  ```
* **Response** (Success - 200):

  ```json
  {
    "refresh": "<refresh_token>",
    "access": "<access_token>",
    "user": {
      "email": "user@example.com",
      "role": "encoder",
      "full_name": "User Full Name",
      // Optional role-specific fields...
    }
  }
  ```
* **Response** (Failure - 401):

  ```json
  {
    "detail": "Invalid credentials"
  }
  ```

---

### Endpoint: **POST** `/api/superadmin/create-encoder/`

* **Description**: Allows superadmin to create an encoder user.
* **Authentication**: Requires `Authorization: Bearer <access_token>` header with superadmin role.
* **Request Body** (JSON):

  ```json
  {
    "email": "encoder@example.com",
    "password": "password123",
    "full_name": "Encoder Name",
    "phone_number": "0912345678",
    "university": "AAU",
    "department": "Computer Science",
    "encoder_type": 1,
    "additional_notes": "Optional notes"
  }
  ```
* **Response** (Success - 201):

  ```json
  {
    "detail": "Encoder created successfully"
  }
  ```
* **Response** (Failure - 403):

  ```json
  {
    "detail": "Only superadmins can create encoders"
  }
  ```

---

### Endpoint: **POST** `/api/encoder/create-student/`

* **Description**: Allows encoder to create a student (student is pending approval).
* **Authentication**: Requires `Authorization: Bearer <access_token>` header with encoder role.
* **Request Body** (JSON):

  ```json
  {
    "email": "student@example.com",
    "password": "password123",
    "full_name": "Student Name",
    "course_program": "Electrical Engineering",
    "graduation_year": 2025,
    "bio": "Optional student bio"
  }
  ```
* **Response** (Success - 201):

  ```json
  {
    "detail": "Student created and pending approval"
  }
  ```

---
