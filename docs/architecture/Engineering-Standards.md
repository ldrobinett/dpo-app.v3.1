# Management Intelligence™ Engineering Standards

**Version:** 1.0  
**Status:** Draft for Review  
**Created:** 2026-07-19  

---

## 1. Purpose

These standards define how Management Intelligence™ is designed, documented, implemented, tested, reviewed, and released. They exist to keep the platform coherent as it grows and to prevent convenience from quietly becoming architecture.

## 2. Authority

Approved specifications, ADRs, and versioned contracts are authoritative.

When implementation conflicts with an approved specification, the implementation is considered incorrect unless the specification is formally revised.

## 3. Architecture Standards

### 3.1 Specification Before Implementation

No material domain, engine, object, API, or workflow should be implemented before its responsibility, boundaries, inputs, outputs, rules, and acceptance criteria are documented.

### 3.2 Single Responsibility

Each domain, service, object, and module must have one clear primary responsibility.

### 3.3 Explicit Ownership

Every business concept must have one authoritative owner. Shared use does not imply shared ownership.

### 3.4 Domain Independence

A domain may consume another domain's published outputs, but it must not reach into that domain's internal calculations or persistence model.

### 3.5 Recommendation Ownership

Only the Recommendation Engine may synthesize and issue final platform recommendations. Domains produce evidence, observations, risks, opportunities, constraints, and forecasts.

### 3.6 UI Separation

Business rules, calculations, threshold logic, and recommendation logic must not exist only in the user interface.

### 3.7 Stable Contracts

Cross-domain and client-facing communication must use documented, versioned contracts.

### 3.8 Explainability by Design

Explainability is not a display feature added later. It is part of every material calculation, inference, and recommendation contract.

## 4. Development Standards

### 4.1 Readability

Code should favor clear intent over clever compression.

### 4.2 Strong Types and Validation

Use explicit types, schema validation, and constrained values where practical. Inputs from external systems are untrusted until validated.

### 4.3 Deterministic Business Logic

Approved business calculations should be deterministic given the same inputs, rules, and version.

### 4.4 No Silent Failure

Missing, stale, invalid, or conflicting data must produce defined behavior, logging, and user-visible limitations when material.

### 4.5 No Duplicated Business Logic

A calculation or business rule must have one canonical implementation. Reuse it through interfaces rather than copying it into another module.

### 4.6 Configuration

Thresholds and business parameters that require operational adjustment should be governed configuration, not unexplained constants buried in code.

### 4.7 Backward Compatibility

Breaking contract changes require a version change, migration plan, and documented consumer impact.

### 4.8 Security

Tenant isolation, least privilege, input validation, secret management, and auditability are required platform behaviors, not optional hardening tasks.

## 5. Data Standards

### 5.1 Source Traceability

Material outputs must retain enough metadata to identify source, time period, transformation version, and freshness.

### 5.2 Time Awareness

Measurements must state their effective period, timezone, grain, and refresh cadence.

### 5.3 Data Quality

Each input must define required fields, validation rules, stale-data thresholds, and failure behavior.

### 5.4 Units and Precision

Units, rounding, and display precision must be explicitly defined and consistently applied.

### 5.5 Historical Reproducibility

Where practical, the system should be able to reproduce a prior conclusion using the data and rule versions effective at that time.

## 6. Testing Standards

### 6.1 Required Test Layers

Use the appropriate combination of:

- Unit tests
- Contract tests
- Integration tests
- Data-quality tests
- Acceptance tests
- Regression tests
- Performance tests
- Security tests

### 6.2 Business Rule Coverage

Every numbered business rule must have at least one positive and one negative test.

### 6.3 Boundary Testing

Tests must cover threshold edges, missing data, stale data, contradictory signals, zero values, extreme values, and invalid states.

### 6.4 Explainability Testing

Tests must verify not only the conclusion but also the evidence and rule trace returned with it.

### 6.5 Release Quality

A feature is not complete while required tests are failing, skipped without approval, or absent.

## 7. Documentation Standards

### 7.1 Required Documentation

Material work may require:

- Domain specification
- ADR
- Object or contract definition
- Session record
- Milestone update
- Migration notes
- Release notes

### 7.2 Document Status

Architecture documents must identify status, version, and revision history.

### 7.3 Current-State Accuracy

Documentation must describe the current approved state. Future ideas belong in clearly labeled roadmap or enhancement sections.

### 7.4 Terminology

Terms defined in the Management Intelligence Glossary must be used consistently.

## 8. ADR Standards

An ADR is required when a decision materially affects:

- Domain boundaries
- Platform ownership
- Data architecture
- Contract compatibility
- Security posture
- Branch or release strategy
- Major technology choice
- Long-term maintainability

An ADR should record context, decision, alternatives, consequences, and status.

## 9. Git Standards

### 9.1 Branch Roles

- `main`: approved production-ready work
- `v40526`: protected Honda Renton beta
- `mi-v5`: active Management Intelligence™ development

### 9.2 Commit Quality

Commits should be focused, understandable, and use an imperative message such as:

`docs: add financial intelligence specification`

### 9.3 No Unreviewed Promotion

Work should not move from `mi-v5` to the beta or production branch without review and defined validation.

### 9.4 Protected History

Do not rewrite shared branch history unless explicitly approved.

## 10. Session Standards

Each material work session should record:

- Session number and date
- Objective
- Decisions made
- Artifacts created or changed
- Commit references
- Open questions
- Next steps

A session is a work record, not proof that a milestone is complete.

## 11. Milestone Standards

Every milestone must define:

- Objective
- Deliverables
- Dependencies
- Exit criteria
- Status
- Approval or review record

Milestones are complete only when exit criteria are satisfied.

## 12. Release Standards

A release requires:

- Approved scope
- Passing required tests
- Security and performance review
- Migration and rollback plan
- Documentation and release notes
- Operational support readiness
- Recorded approval

## 13. Naming Standards

Names should be explicit, stable, and aligned with the glossary.

Avoid:

- Unexplained abbreviations
- Generic names such as `data`, `helper`, or `manager` when a precise name exists
- Different names for the same concept
- The same name for materially different concepts

## 14. Versioning Standards

Specifications, contracts, and releases must use intentional versioning.

A version change should communicate whether the change is:

- Editorial
- Backward-compatible
- Behavior-changing
- Breaking

## 15. Observability Standards

Material services and intelligence calculations should expose:

- Structured logs
- Errors and failure reasons
- Latency and throughput
- Data freshness
- Calculation version
- Confidence and limitation metadata
- Audit identifiers

## 16. Review Standards

Reviewers should evaluate:

- Correctness
- Domain ownership
- Boundary integrity
- Security
- Explainability
- Test adequacy
- Contract impact
- Operational usefulness
- Documentation accuracy

## 17. Definition of Done

Work is done only when:

- The approved requirement is met.
- Ownership and boundaries remain intact.
- Required tests pass.
- Failure behavior is defined.
- Explainability requirements are satisfied.
- Documentation is current.
- Review comments are resolved.
- The change is committed to the correct branch.

## 18. Exceptions

Exceptions must be explicit, temporary when possible, documented with rationale, and assigned an owner and resolution date. Undocumented exceptions are simply defects with better public relations.

## 19. Revision History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-07-19 | Initial engineering standards created during Session 009 |
