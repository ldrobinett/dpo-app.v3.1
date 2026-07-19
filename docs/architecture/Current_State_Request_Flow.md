# Current-State Request Flow

**System:** ProdTracker V40526  
**Document Status:** Current-State Architecture  
**Session:** 003  
**Created:** July 19, 2026

## Purpose

This document explains how a browser request moves through ProdTracker from application startup to the rendered Home Dashboard.

## High-Level Request Flow

```text
Developer runs python run.py
        |
        v
run.py imports create_app()
        |
        v
app.py creates and configures Flask
        |
        v
Flask extensions are initialized
        |
        v
Blueprints are registered
        |
        v
Local server starts on port 5001
        |
        v
Browser requests /
        |
        v
Flask resolves main.home
        |
        v
Flask-Login checks authentication
        |
        v
Home route identifies user type and store
        |
        v
Database records are retrieved
        |
        v
Business calculations are performed
        |
        v
Recommendations and dashboard values are created
        |
        v
home.html is rendered
        |
        v
HTML response is returned to the browser