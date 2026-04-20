# FINAL README - Six Vulnerability Fixes

This document logs the final work done in `Vulnerable Fix Code`.

Only the six requested vulnerabilities were fixed:

1. SQL injection risk
2. Password brute forcing
3. Role-based access control
4. Password strength
5. Email validation
6. Hardcoded secret key

The other vulnerabilities from the earlier 14-fix version were intentionally left unfixed.

## Files Changed

| File | Purpose |
|------|---------|
| `app/config.py` | Loads `SECRET_KEY` from `.env` instead of hardcoding it |
| `app/extensions.py` | Adds Flask-Limiter |
| `app/__init__.py` | Initializes Flask-Limiter |
| `app/account/routes.py` | Adds login rate limit, generic login error, password rules, email checks |
| `app/account/forms.py` | Adds WTForms email validator |
| `app/dashboard/routes.py` | Adds admin/super-admin role checks |
| `requirements_new.txt` | Adds dependencies for limiter and email validation |
| `.env` | Stores runtime secret key |

## 1. SQL Injection Risk

The project uses SQLAlchemy ORM queries and Flask integer route converters instead of raw SQL string building. User-controlled values are passed through ORM filters such as:

```python
Blog_User.query.filter_by(email=email).first()
Blog_Posts.query.get_or_404(id)
```

How to check:

```bash
rg -n "execute\(|text\(|SELECT|INSERT|UPDATE|DELETE" app create_db.py
```

The application should not contain unsafe raw SQL queries built from user input.

## 2. Password Brute Forcing

The login route in `app/account/routes.py` is limited to 5 attempts per minute:

```python
@limiter.limit("5 per minute")
```

It also uses one generic failure message:

```python
Invalid credentials, please try again.
```

How to check:

1. Run the app.
2. Open `/login`.
3. Submit wrong credentials more than five times in one minute.
4. Extra attempts should be temporarily blocked.

## 3. Role-Based Access Control

The sensitive user-management routes in `app/dashboard/routes.py` now require `admin` or `super_admin`:

```python
if current_user.type not in ("admin", "super_admin"):
    abort(403)
```

Protected routes:

- `/dashboard/manage_users/update/<id>`
- `/dashboard/manage_users/delete/<id>`
- `/dashboard/manage_users/block/<id>`

How to check:

1. Log in as a regular user.
2. Visit `/dashboard/manage_users/update/4`.
3. You should receive `403 Forbidden`.
4. Log in as admin and retry. The route should be allowed.

## 4. Password Strength

New signup passwords must:

- Be at least 8 characters
- Contain at least one uppercase letter
- Contain at least one digit

How to check:

1. Open `/signup`.
2. Try `password`. It should fail.
3. Try `Password1`. It should pass the password checks.

## 5. Email Validation

Email validation was added in:

- `app/account/forms.py` with `Email()`
- `app/account/routes.py` with a server-side regex check

How to check:

1. Open `/signup`.
2. Try `not-an-email`. It should be rejected.
3. Try `test@example.com`. It should pass validation.

## 6. Hardcoded Secret Key

The old hardcoded key was removed:

```python
SECRET_KEY = "myFlaskApp4Fun"
```

The fixed version uses:

```python
SECRET_KEY = os.getenv("SECRET_KEY")
```

If `SECRET_KEY` is missing, the app raises an error at startup.

How to check:

1. Open `.env`.
2. Confirm `SECRET_KEY=<random-secret-value>` exists.
3. Temporarily remove it.
4. Run `python run.py`.
5. Startup should fail with a missing `SECRET_KEY` error.

## Intentionally Unfixed Vulnerabilities

These were not part of the requested six and were left vulnerable:

- IDOR on own-account update/delete/profile-picture routes
- Stored XSS in CKEditor post body
- Missing CSRF protection on JSON API endpoints
- Unauthenticated or unauthorized comment/reply deletion
- Missing session timeout and secure cookie flags
- Missing HTTP security headers
- Client-side file size validation bypass
- Contact form rate limiting
- Verbose contact-form exception disclosure

## How to Run

Open the fixed project:

```bash
cd "d:\Ajay Ireland\Vulnerable Fix Code"
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements_new.txt
```

Make sure `.env` contains:

```env
SECRET_KEY=<random-secret-value>
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
```

Run the app:

```bash
python run.py
```

Open:

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

Note: seeded accounts may not satisfy the new password-strength rule because they were created before the new rule. The password-strength rule applies to new signups.

