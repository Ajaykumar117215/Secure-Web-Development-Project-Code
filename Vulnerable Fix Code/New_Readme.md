# Final Security Fix Log

This folder contains the fixed version of the Flask travel blog project. Only the six requested vulnerabilities were fixed:

1. SQL injection risk
2. Password brute forcing
3. Role-based access control
4. Password strength
5. Email validation
6. Hardcoded secret key

All other vulnerabilities from the original vulnerable project were intentionally left unfixed for assessment comparison.

## What Was Changed

### 1. SQL Injection Risk

**Files checked:** `app/account/routes.py`, `app/website/routes.py`, `app/dashboard/routes.py`

The application uses SQLAlchemy ORM queries instead of building SQL strings from user input. Route parameters such as post IDs and user IDs are also constrained with Flask integer route converters such as `<int:id>` and `<int:index>`.

This prevents attacker-controlled values from being concatenated into raw SQL statements.

**How to check:**

- Search the fixed folder for raw SQL execution:

```bash
rg -n "execute\(|text\(|SELECT|INSERT|UPDATE|DELETE" app create_db.py
```

- User input should be handled through SQLAlchemy filters such as:

```python
Blog_User.query.filter_by(email=email).first()
Blog_Posts.query.get_or_404(id)
```

### 2. Password Brute Forcing

**Files changed:**

- `app/extensions.py`
- `app/__init__.py`
- `app/account/routes.py`
- `requirements_new.txt`

The login route is now rate-limited with Flask-Limiter:

```python
@limiter.limit("5 per minute")
```

The login error message was also changed to a generic message:

```python
Invalid credentials, please try again.
```

This prevents attackers from making unlimited login attempts and reduces email/user enumeration through different login errors.

**How to check:**

1. Run the app.
2. Go to `/login`.
3. Submit wrong login details more than five times in one minute.
4. The app should start blocking additional attempts temporarily.

### 3. Role-Based Access Control

**File changed:** `app/dashboard/routes.py`

Admin user-management routes now require the logged-in user to be either `admin` or `super_admin`.

Protected routes:

- `/dashboard/manage_users/update/<id>`
- `/dashboard/manage_users/delete/<id>`
- `/dashboard/manage_users/block/<id>`

Fix used:

```python
if current_user.type not in ("admin", "super_admin"):
    abort(403)
```

**How to check:**

1. Log in as a regular user.
2. Try to directly open `/dashboard/manage_users/update/4`.
3. You should receive HTTP `403 Forbidden`.
4. Log in as an admin and try the same route. It should be accessible.

### 4. Password Strength

**File changed:** `app/account/routes.py`

The signup route now rejects weak passwords. New passwords must:

- Be at least 8 characters long
- Include at least one uppercase letter
- Include at least one digit

**How to check:**

1. Go to `/signup`.
2. Try `password` as the password. It should be rejected.
3. Try `Password1`. It should pass the strength checks.

### 5. Email Validation

**Files changed:**

- `app/account/forms.py`
- `app/account/routes.py`
- `requirements_new.txt`

Email validation was added in two places:

- WTForms `Email()` validator
- Server-side signup route regex check

This prevents invalid signup email values such as `abc`, `test@`, or `test.com`.

**How to check:**

1. Go to `/signup`.
2. Enter an invalid email such as `not-an-email`.
3. The application should reject it.
4. Enter a valid email such as `test@example.com`.

### 6. Hardcoded Secret Key

**Files changed:**

- `app/config.py`
- `.env`

The original hardcoded Flask secret key was removed from source code:

```python
SECRET_KEY = "myFlaskApp4Fun"
```

The fixed version loads the key from the environment:

```python
SECRET_KEY = os.getenv("SECRET_KEY")
```

If `SECRET_KEY` is missing, the application stops at startup with a clear error.

**How to check:**

1. Open `.env`.
2. Confirm it contains:

```env
SECRET_KEY=<random-secret-value>
```

3. Temporarily remove or rename the key.
4. Run the app. It should fail with a `SECRET_KEY environment variable is not set` error.

## Vulnerabilities Intentionally Left Unfixed

The following security issues from the previous 14-fix version were intentionally reverted or left vulnerable because they were not part of the requested six:

- IDOR on own account update/delete/profile picture routes
- Stored XSS in CKEditor blog post body
- Missing CSRF protection on JSON API endpoints
- Unauthenticated or unauthorized comment/reply deletion
- Session timeout and secure cookie flags
- HTTP security headers
- Server-side file size validation for uploads
- Contact form rate limiting
- Generic error handling for contact form exceptions

## How to Run the Code

### 1. Open the fixed project folder

```bash
cd "d:\Ajay Ireland\Vulnerable Fix Code"
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements_new.txt
```

### 4. Check the `.env` file

The project root should contain:

```env
SECRET_KEY=<random-secret-value>
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
```

`SECRET_KEY` is required. Email values are only needed if you want contact-form email sending to work.

### 5. Run the Flask app

```bash
python run.py
```

### 6. Open the app

```text
http://127.0.0.1:5000
```

## Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Super Admin | `super@admin` | `admin123` |
| Admin | `r@r` | `user123` |
| Author | `e@e` | `user123` |
| Regular User | `j@m` | `user123` |

Existing seeded passwords may not meet the new password-strength rule because they were created before the rule was added. The password-strength fix applies to new signups.

