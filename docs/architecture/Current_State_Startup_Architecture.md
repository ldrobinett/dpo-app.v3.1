# Current-State Startup Architecture

**System:** ProdTracker V40526  
**Document Status:** Initial Current-State Map  
**Created:** July 18, 2026

## Purpose

This document explains how ProdTracker starts locally and how the major application components are assembled.

## Application Entry Point

The local application is started from PowerShell with:

`python run.py`

The `run.py` file is the executable entry point for local development.

It imports the `create_app()` function from `app.py`, creates the configured Flask application, and starts the development server.

The `app.py` file contains the application factory and the main assembly logic.

## Startup Sequence

1. The developer runs `python run.py` from PowerShell.
2. Python executes `run.py`.
3. `run.py` imports `create_app()` from `app.py`.
4. `run.py` calls `create_app()`.
5. `create_app()` creates the Flask application.
6. Core configuration and the secret key are loaded.
7. The application ensures the local `instance` directory exists.
8. ProdTracker determines which database connection to use.
9. Flask extensions are initialized.
10. Flask-Login behavior is configured.
11. Application blueprints are imported.
12. Each blueprint is registered with the Flask application.
13. The configured application is returned to `run.py`.
14. `run.py` starts the local Flask development server.

## Database Selection

ProdTracker supports two database paths.

### Configured Environment

When the `DATABASE_URL` environment variable exists, ProdTracker uses that database connection.

### Local Development

When `DATABASE_URL` does not exist, ProdTracker uses:

`instance/site.db`

This allows local development to operate independently from the hosted application database.

## Flask Extensions

ProdTracker initializes the following extensions:

- SQLAlchemy through `db`
- Flask-Login through `login_manager`
- Flask-Bcrypt through `bcrypt`
- Flask-Migrate through `Migrate`

These extension objects are defined separately and attached to the Flask application during startup.

## Registered Blueprints

The current application registers these blueprints:

- Main
- Authentication
- Teams
- Schedule
- Finance
- Worklog
- Labor Matrix
- Route Sheet
- Calculators
- Onboarding
- Reconciliation
- Operator
- Users

Each blueprint owns a functional section of ProdTracker.

## Current-State Flow

python run.py
    |
    v
run.py
    |
    +-- import create_app from app.py
    |
    +-- call create_app()
    |
    v
app.py / create_app()
    |
    +-- create Flask application
    |
    +-- load configuration
    |
    +-- select database
    |
    +-- initialize extensions
    |
    +-- configure authentication
    |
    +-- register blueprints
    |
    v
return configured application
    |
    v
run.py starts Flask server

run.py = ignition switch
app.py = assembly plant

## Questions
- Flask-Login currently has a user loader defined in both `extensions.py`
  and `app.py`. Determine which implementation is active and consolidate
  them during a future controlled refactor.

 ## Local Development Entry Point

ProdTracker is started locally from PowerShell with:

`python run.py`

The `run.py` module performs the following actions:

1. Imports `create_app()` from `app.py`.
2. Calls `create_app()` to assemble the Flask application.
3. Starts the Flask development server.
4. Uses port `5001`.
5. Enables debug mode.
6. Enables automatic restart when Python files change.

The typical local address is:

`http://127.0.0.1:5001` 