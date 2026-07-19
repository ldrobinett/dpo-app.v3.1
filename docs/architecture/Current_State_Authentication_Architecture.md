# Current-State Authentication Architecture

**System:** ProdTracker V40526  
**Document Status:** Current-State Architecture  
**Session:** 004  
**Created:** July 19, 2026

---

# Purpose

This document describes how ProdTracker authenticates users, establishes authenticated sessions, and routes users to the appropriate dashboard.

No architectural changes are proposed. This document reflects the current implementation.

---

# Authentication Flow

```text
Browser
    │
    ▼
GET /login
    │
    ▼
Display Login Form
    │
    ▼
User submits credentials
    │
    ▼
POST /login
    │
    ▼
Validate LoginForm
    │
    ▼
Retrieve User
    │
    ▼
Verify Password (bcrypt)
    │
    ▼
login_user()
    │
    ▼
Flask Session Created
    │
    ▼
Redirect
    │
    ▼
Home Dashboard
```

---

# Login Route Responsibilities

The login route performs only orchestration.

Its responsibilities are:

1. Prevent already authenticated users from logging in again.
2. Instantiate the login form.
3. Validate submitted data.
4. Retrieve the user from the database.
5. Verify the supplied password using bcrypt.
6. Create an authenticated Flask session.
7. Redirect the user to the requested page or Home.
8. Display an error message when authentication fails.

The route intentionally contains very little business logic.

---

# Login Form

The route creates:

```python
form = LoginForm()
```

The template is responsible for rendering the form.

This maintains separation between presentation and controller logic.

---

# Form Validation

Authentication proceeds only when:

```python
form.validate_on_submit()
```

returns True.

This confirms:

- Request is POST
- Form validation succeeds

---

# User Lookup

Users are retrieved by username.

```python
User.query.filter_by(username=username).first()
```

If no matching user exists, authentication fails.

---

# Password Verification

Passwords are never compared directly.

The stored bcrypt hash is compared against the submitted password using:

```python
bcrypt.check_password_hash(...)
```

This prevents plaintext password storage.

---

# Session Creation

Successful authentication occurs when:

```python
login_user(user)
```

is called.

Flask-Login then creates the authenticated session.

The authenticated user becomes available through:

```python
current_user
```

throughout the application.

---

# Remember Me

If selected, the login session persists using Flask-Login's remember functionality.

---

# Safe Redirect

The application retrieves:

```python
request.args.get("next")
```

and validates the destination using:

```python
_safe_next_url()
```

This protects against open redirect attacks.

---

# User Types

ProdTracker supports two authenticated user models.

## Store Users

Represent dealership personnel.

Characteristics:

- Assigned to one Managed Store
- Standard application users
- `is_operator == False`
- Session identifier format:

```
u:<id>
```

---

## Operator Users

Represent platform administrators.

Characteristics:

- Global platform access
- `is_operator == True`
- Session identifier format:

```
op:<id>
```

The prefixed identifier allows Flask-Login to determine which table to query when restoring a session.

---

# Authentication Lifecycle

```text
Browser
    │
    ▼
Login Page
    │
    ▼
Credentials Submitted
    │
    ▼
Database Lookup
    │
    ▼
Password Verification
    │
    ▼
Authenticated Session
    │
    ▼
current_user Available
    │
    ▼
Protected Routes
```

---

# Architectural Observations

Authentication responsibilities are appropriately separated.

Current strengths include:

- Thin controller
- Secure password verification
- Safe redirect validation
- Session abstraction through Flask-Login
- Separate Store User and Operator User models
- Role/Capability framework prepared for future authorization expansion

---

# V5 Considerations

The existing authentication architecture is compatible with future Management Intelligence development.

No modifications are recommended during the architecture discovery phase.

Future enhancements should build upon the existing authentication layer rather than replace it.