# ADR-001
## Current Dashboard Architecture

### Status

Accepted

### Observation

The current Home Dashboard performs significant business calculations inside the route before rendering the template.

The route acts as both:

- Controller
- Analytics Engine

The route gathers data, performs business calculations, creates recommendations, calculates pacing, and finally renders the dashboard.

### Benefits

Simple execution path.

Easy debugging.

All calculations visible in one location.

### Limitations

As Management Intelligence expands, this route will become increasingly difficult to maintain.

Business intelligence calculations should eventually migrate into dedicated service classes while leaving the route responsible only for:

- Authentication
- Data orchestration
- Template rendering

### V5 Direction

Future Management Intelligence calculations should be implemented in independent service modules rather than expanding the Home route.