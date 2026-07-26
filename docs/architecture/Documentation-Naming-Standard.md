# Documentation Naming Standard

## Purpose

This standard establishes one consistent naming convention for Management Intelligence v5 documentation. The goal is to make the repository easy to navigate, reduce duplicate documents, and prevent filenames from becoming another archaeological dig performed by increasingly annoyed humans.

## Canonical Convention

Use **Title-Case words separated by hyphens** for general Markdown documentation.

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

Session documents are the sole exception to the general hyphen convention. They use the prefix `Session_` followed by a zero-padded three-digit sequence:

- `Session_001.md`
- `Session_002.md`
- `Session_008.md`
- `Session_013.md`

Do not use a hyphen after `Session`, inconsistent digit counts, spaces, or descriptive suffixes in the filename.

### Incorrect

- `Session-008.md`
- `Session_8.md`
- `session_008.md`
- `Session_008_Architecture.md`

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