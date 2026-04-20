# Vulnerabilities in Vulnerable Code

This file lists only the vulnerabilities present in the `Vulnerable Code` version of the Flask travel blog application.

## V-00 - Demonstrable SQL Injection on Login

**Affected files:** `app/account/routes.py`, `app/templates/account/login.html`

**Category:** OWASP A03:2021 Injection  
**CWE:** CWE-89 SQL Injection  
**Severity:** High

The login route contains an intentionally unsafe raw SQL query built with user-controlled `email` and `password` values. Because the login email field is rendered as `type="text"`, SQL payloads can be submitted directly through the browser.

```python
raw_sql = f"SELECT id FROM blog_user WHERE email = '{email}' AND password = '{password}' LIMIT 1"
injected_user = db.session.execute(text(raw_sql)).mappings().first()
```

An attacker can enter the following payload in the email field and any value in the password field:

```text
' OR 1=1 -- 
```

This changes the SQL logic so the condition is always true and logs the attacker in as the first user returned by the database.

## V-01 - Hardcoded Secret Key

**Affected file:** `app/config.py`

**Category:** OWASP A05:2021 Security Misconfiguration  
**CWE:** CWE-798 Use of Hard-coded Credentials  
**Severity:** Critical

The Flask `SECRET_KEY` is hardcoded directly in source code.

```python
SECRET_KEY = "myFlaskApp4Fun"
```

Flask uses this value to sign session data. If the key is known or leaked, an attacker may be able to forge or tamper with signed application data.

## V-02 - IDOR on Account Update

**Affected file:** `app/account/routes.py`

**Category:** OWASP A01:2021 Broken Access Control  
**CWE:** CWE-639 Authorization Bypass Through User-Controlled Key  
**Severity:** High

The account update route accepts a user-controlled `id` value and loads that user record without confirming that it belongs to the currently authenticated user.

```python
@account.route("/dashboard/manage_account/update/<int:id>", methods=["GET", "POST"])
@login_required
def update_own_acct_info(id):
    user_at_hand = Blog_User.query.get_or_404(id)
```

Any logged-in user can change the URL parameter to target another user's account and modify that user's profile data.

## V-03 - Missing Role-Based Authorization on Admin User Routes

**Affected file:** `app/dashboard/routes.py`

**Category:** OWASP A01:2021 Broken Access Control  
**CWE:** CWE-285 Improper Authorization  
**Severity:** High

Sensitive user-management routes are protected only by `@login_required`. They do not verify that the current user is an admin or super admin.

```python
@dashboard.route("/dashboard/manage_users/update/<int:id>", methods=["GET", "POST"])
@login_required
def user_update(id):
```

The affected operations include updating users, deleting users and blocking users. A normal authenticated user who knows the URL can attempt privileged actions.

## V-04 - No Brute Force Protection on Login

**Affected file:** `app/account/routes.py`

**Category:** OWASP A07:2021 Identification and Authentication Failures  
**CWE:** CWE-307 Improper Restriction of Excessive Authentication Attempts  
**Severity:** High

The login route has no rate limiting, account lockout or delay after failed attempts. An attacker can repeatedly submit login attempts without restriction.

The route also reveals different messages for an invalid email and an invalid password:

```python
flash("This email does not exist in our database.")
flash("Incorrect password, please try again.")
```

These distinct messages allow account enumeration because attackers can determine whether an email exists.

## V-05 - No Password Complexity Enforcement

**Affected files:** `app/account/routes.py`, `app/account/forms.py`

**Category:** OWASP A07:2021 Identification and Authentication Failures  
**CWE:** CWE-521 Weak Password Requirements  
**Severity:** Medium

The signup process accepts weak passwords. The password is taken directly from `request.form` and there is no minimum length, complexity rule or confirmation check.

```python
password=hash_pw(request.form.get("password"))
```

This allows users to create accounts with easily guessed passwords.

## V-06 - Stored XSS Through CKEditor Blog Post Body

**Affected files:** `app/dashboard/routes.py`, post rendering templates

**Category:** OWASP A03:2021 Injection  
**CWE:** CWE-79 Cross-Site Scripting  
**Severity:** High

Blog post body content is accepted from CKEditor and stored without server-side sanitization.

```python
post = Blog_Posts(..., body=form.body.data, ...)
```

Because rich HTML is later rendered in the post view, an author can store malicious script content that executes when other users view the post.

## V-07 - Missing CSRF Protection on JSON API Endpoints

**Affected file:** `app/website/routes.py`

**Category:** OWASP A01:2021 Broken Access Control  
**CWE:** CWE-352 Cross-Site Request Forgery  
**Severity:** Medium

JSON endpoints for actions such as commenting, replying, liking and bookmarking accept state-changing POST requests without verifying a CSRF token.

```python
data = request.get_json()
```

A malicious site could cause an authenticated user's browser to submit unwanted actions to these endpoints.

## V-08 - Unauthenticated Comment and Reply Deletion

**Affected file:** `app/website/routes.py`

**Category:** OWASP A01:2021 Broken Access Control  
**CWE:** CWE-862 Missing Authorization  
**Severity:** High

The comment and reply deletion endpoint does not require login and does not verify ownership of the content being deleted.

```python
@website.route("/delete_comment_or_reply/<int:index>", methods=["POST"])
def post_delete_comment(index):
```

Anyone who can send a crafted POST request with a valid comment or reply identifier may delete content belonging to another user.

## V-09 - No Email Format Validation at Signup

**Affected files:** `app/account/routes.py`, `app/account/forms.py`

**Category:** OWASP A07:2021 Identification and Authentication Failures  
**CWE:** CWE-1286 Improper Validation of Syntactic Correctness of Input  
**Severity:** Low

Signup accepts any string as an email address. The account form uses `DataRequired()` but does not use an email format validator.

```python
email = StringField("Email", validators=[DataRequired()])
```

Invalid values such as `notanemail` can be stored as account email addresses.

## V-10 - No Session Timeout Configuration

**Affected file:** `app/config.py`

**Category:** OWASP A07:2021 Identification and Authentication Failures  
**CWE:** CWE-613 Insufficient Session Expiration  
**Severity:** Medium

The application does not configure a server-side session lifetime. Authenticated sessions may remain valid longer than intended, especially on shared or unattended devices.

No configuration such as `PERMANENT_SESSION_LIFETIME` is present.

## V-11 - Missing HTTP Security Headers

**Affected files:** `app/__init__.py`, `app/config.py`

**Category:** OWASP A05:2021 Security Misconfiguration  
**CWE:** CWE-693 Protection Mechanism Failure  
**Severity:** Medium

The application does not set common browser security headers, including:

- `Content-Security-Policy`
- `X-Frame-Options`
- `X-Content-Type-Options`
- `Referrer-Policy`
- `Strict-Transport-Security`

The absence of these headers increases exposure to browser-based attacks such as clickjacking, MIME sniffing and script injection impact.

## V-12 - Client-Side File Size Validation Bypass

**Affected file:** `app/dashboard/routes.py`

**Category:** OWASP A05:2021 Security Misconfiguration  
**CWE:** CWE-434 Unrestricted Upload of File with Dangerous Type  
**Severity:** Medium

Blog image upload size checks rely on size values submitted by the client.

```python
if form.picture_v.data and int(form.picture_v_size.data) < 1500000:
```

Because the size field is client-controlled, an attacker can submit a falsified value and bypass the intended per-image size restriction.

## V-13 - No Rate Limiting on Contact Form

**Affected file:** `app/website/routes.py`

**Category:** OWASP A05:2021 Security Misconfiguration  
**CWE:** CWE-770 Allocation of Resources Without Limits or Throttling  
**Severity:** Low

The public contact form accepts unauthenticated submissions without rate limiting. Each submission can write to the database and trigger email-sending behavior.

An attacker can automate submissions to spam the application, fill the contact table or abuse outbound email functionality.

## V-14 - Verbose Exception Disclosure on Contact Form Error

**Affected file:** `app/website/routes.py`

**Category:** OWASP A05:2021 Security Misconfiguration  
**CWE:** CWE-209 Generation of Error Message Containing Sensitive Information  
**Severity:** Medium

The contact form error handler returns raw exception details to the client.

```python
except Exception as e:
    return f"There was an error adding message to the database: {str(e)}"
```

If an error occurs, internal database or application details may be exposed in the HTTP response.

## Summary

| ID | Vulnerability | Severity |
|----|---------------|----------|
| V-00 | Demonstrable SQL Injection on Login | High |
| V-01 | Hardcoded Secret Key | Critical |
| V-02 | IDOR on Account Update | High |
| V-03 | Missing Role-Based Authorization on Admin User Routes | High |
| V-04 | No Brute Force Protection on Login | High |
| V-05 | No Password Complexity Enforcement | Medium |
| V-06 | Stored XSS Through CKEditor Blog Post Body | High |
| V-07 | Missing CSRF Protection on JSON API Endpoints | Medium |
| V-08 | Unauthenticated Comment and Reply Deletion | High |
| V-09 | No Email Format Validation at Signup | Low |
| V-10 | No Session Timeout Configuration | Medium |
| V-11 | Missing HTTP Security Headers | Medium |
| V-12 | Client-Side File Size Validation Bypass | Medium |
| V-13 | No Rate Limiting on Contact Form | Low |
| V-14 | Verbose Exception Disclosure on Contact Form Error | Medium |
