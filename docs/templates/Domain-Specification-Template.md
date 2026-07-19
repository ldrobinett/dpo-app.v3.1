# Management Intelligence™ Domain Specification Template

**Document Status:** Draft | Review | Approved | Superseded  
**Version:** 1.0  
**Domain Owner:**  
**Last Updated:**  
**Related ADRs:**  
**Related Domains:**  

---

## 1. Purpose

State why the domain exists and the management problem it is intended to solve.

## 2. Mission

Define the domain's single, enduring responsibility in one clear statement.

## 3. Business Problem

Describe the operational or management condition that requires this domain. Explain why reporting alone is insufficient.

## 4. Business Value

Describe the decisions, outcomes, or behaviors this domain improves.

## 5. Domain Boundary

### 5.1 This Domain Owns

List the concepts, calculations, observations, signals, and intelligence outputs owned by this domain.

### 5.2 This Domain Does Not Own

List neighboring concepts intentionally assigned to other domains or engines.

### 5.3 Boundary Rules

Define rules that prevent duplicated logic, conflicting ownership, or leakage into the UI, API, or Recommendation Engine.

## 6. Inputs

For each input, document:

| Input | Description | Source | Frequency | Required | Data Quality Rule |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## 7. Core Measurements

For each directly observed or calculated measurement, document:

| Measurement | Definition | Formula | Unit | Grain | Time Window | Owner |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

## 8. Derived Intelligence

Describe the conclusions created by combining measurements, context, thresholds, trends, and domain rules.

| Intelligence Output | Meaning | Inputs | Logic | Confidence Requirement |
|---|---|---|---|---|
|  |  |  |  |  |

## 9. Health Indicators

Define indicators that describe whether the domain is operating within an acceptable or sustainable range.

## 10. Risk Indicators

Define conditions that expose performance, capacity, financial, customer, or organizational risk.

Each risk indicator should include:

- Trigger condition
- Severity logic
- Evidence required
- Time sensitivity
- Clear condition
- Responsible downstream consumer

## 11. Opportunity Indicators

Define conditions showing realistic, actionable upside.

Each opportunity indicator should include:

- Opportunity condition
- Supporting evidence
- Estimated impact
- Required capacity or constraint check
- Expiration or review window

## 12. Business Rules

Number each rule using the format `BR-[DOMAIN]-###`.

Example:

> **BR-XXX-001:** A domain must not classify a condition as an opportunity unless the required operating capacity exists.

## 13. Domain Objects

Document the objects created, consumed, or enriched by the domain.

| Object | Purpose | Key Attributes | Source of Truth | Lifecycle |
|---|---|---|---|---|
|  |  |  |  |  |

## 14. Interfaces

### 14.1 Consumes

List events, services, APIs, datasets, and domain outputs consumed.

### 14.2 Produces

List measurements, observations, signals, risks, opportunities, forecasts, and explanations produced.

### 14.3 Contract Rules

Define schemas, required fields, error behavior, versioning expectations, and compatibility rules.

## 15. Recommendation Engine Interaction

This section defines what the domain may submit to the Recommendation Engine.

The domain may produce:

- Observations
- Evidence
- Risks
- Opportunities
- Constraints
- Forecasts
- Confidence levels
- Explanations

The domain does **not** produce final recommendations unless an approved ADR explicitly changes that platform rule.

## 16. Dependencies

Document upstream data, shared services, other domains, reference data, and platform capabilities required for correct operation.

## 17. Data Quality and Failure Behavior

Define:

- Missing-data behavior
- Stale-data thresholds
- Invalid-data handling
- Partial-calculation rules
- Confidence degradation
- User-visible explanation requirements

## 18. Explainability Requirements

Every material output must be traceable to:

1. Source data
2. Applied business rules
3. Calculation or inference logic
4. Time window
5. Confidence level
6. Known limitations

## 19. Security and Access

Describe tenant boundaries, role access, sensitive fields, audit requirements, and prohibited exposure.

## 20. Acceptance Tests

Use test identifiers in the format `AT-[DOMAIN]-###`.

Each test must define:

- Given
- When
- Then
- Required data
- Expected result
- Failure result

## 21. Worked Examples

Provide realistic examples showing:

- Normal operation
- Positive opportunity
- Material risk
- Missing or stale data
- Conflicting signals
- Cross-domain interaction

## 22. Observability

Define logs, metrics, traces, data-quality alerts, calculation audits, and operational dashboards required to support the domain.

## 23. Performance Requirements

Document latency, throughput, refresh cadence, scale assumptions, and acceptable degradation behavior.

## 24. Open Questions

Track unresolved issues that do not yet justify an ADR.

## 25. Future Enhancements

Capture ideas outside the approved scope without allowing them to quietly become requirements, humanity's favorite project-management trick.

## 26. Revision History

| Version | Date | Author | Change | Approval |
|---|---|---|---|---|
| 1.0 |  |  | Initial specification |  |

---

## Completion Checklist

A domain specification is ready for implementation only when:

- [ ] Purpose and mission are clear
- [ ] Ownership boundaries are explicit
- [ ] Inputs and measurements are defined
- [ ] Derived intelligence is explainable
- [ ] Risks and opportunities are testable
- [ ] Business rules are numbered
- [ ] Interfaces are versionable
- [ ] Failure behavior is defined
- [ ] Acceptance tests are complete
- [ ] Dependencies are acknowledged
- [ ] Security and observability requirements are documented
- [ ] Review and approval are recorded
