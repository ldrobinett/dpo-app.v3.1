# Documentation Naming Standard

## Purpose

This standard establishes one consistent naming convention for Management Intelligence v5 documentation. The goal is to make the repository easy to navigate, reduce duplicate documents, and prevent filenames from becoming another archaeological dig performed by increasingly annoyed humans.

## Canonical Convention

Use **Title-Case words separated by hyphens** for Markdown documentation.

### Correct

- `Management-Decision-Architecture.md`
- `Recommendation-Engine.md`
- `Organizational-Learning.md`
- `Executive-Workspace.md`

### Incorrect

- `management decision architecture.md`
- `Management_Decision_Architecture.md`
- `management-decision-architecture.md`
- `ManagementDecisionArchitecture.md`

## Session Documents

Session documents use a three-digit sequence:

- `Session-001.md`
- `Session-002.md`
- `Session-013.md`

Do not use underscores, inconsistent digit counts, or descriptive suffixes in the filename.

## Versioning

Do not place version history in filenames.

### Prohibited

- `Architecture-v2.md`
- `Architecture-final.md`
- `Architecture-final-final.md`
- `main.py.2.py`
- `home.html.v1.html`

Git provides version history. A second version inside the filename creates two competing systems for remembering the past, because apparently one was not enough.

## Folder Naming

Use lowercase folder names with hyphens only when more than one word is required.

### Examples

- `docs/architecture/`
- `docs/sessions/`
- `docs/work-orders/`
- `docs/post-mvp/`

## Canonical Document Rule

Each architectural subject must have one canonical document.

When overlapping documents are discovered:

1. Identify the most complete and current document.
2. Merge any unique relevant material into it.
3. Update references to point to the canonical document.
4. Delete the obsolete duplicate.

## Rename Procedure

GitHub's contents API does not provide a direct rename operation. A rename is performed as one controlled change:

1. Create the correctly named file with the complete original content.
2. Verify the new file.
3. Delete the incorrectly named file.
4. Update links and references.

No document should be deleted until its replacement has been verified.

## Scope

This standard applies to:

- Architecture documents
- Session records
- Work orders
- Roadmaps
- Operating-model documentation
- Product and implementation specifications

Source-code naming continues to follow the conventions of its language and framework.

## Effective Date

Effective immediately for the `mi-v5` branch.
