# Current-State Extensions Architecture

**System:** ProdTracker V40526  
**Document Status:** Initial Current-State Map  
**Created:** July 18, 2026

## Purpose

This document explains how ProdTracker creates and initializes shared Flask extensions.

## Extensions Module

The shared Flask extension objects are created in:

`extensions.py`

The module creates the following objects:

- `db`
- `login_manager`
- `bcrypt`
- `migrate`

These objects are created without an application instance.

## Extension Responsibilities

### SQLAlchemy

`db = SQLAlchemy()`

Provides database access, model mapping, queries, and database sessions.

### Flask-Login

`login_manager = LoginManager()`

Handles authenticated user sessions and redirects unauthenticated users to the login page.

### Flask-Bcrypt

`bcrypt = Bcrypt()`

Provides password hashing and password verification.

### Flask-Migrate

`migrate = Migrate()`

Supports controlled database schema changes through migration files.

## Initialization Flow

```text
extensions.py
    |
    +-- create db
    +-- create login_manager
    +-- create bcrypt
    +-- create migrate
    |
    v
app.py imports extension objects
    |
    +-- db.init_app(app)
    +-- bcrypt.init_app(app)
    +-- login_manager.init_app(app)
    +-- Migrate(app, db)
    |
    v
extensions become attached to ProdTracker