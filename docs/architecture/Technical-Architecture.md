# Technical Architecture

## Purpose

This document defines the technical architecture for the ProdTracker Management Decision Platform, Management Intelligence v5. It establishes the structural model for how operational data becomes business meaning, management insight, recommended action, and measurable execution.

The architecture is designed around one central principle:

> Reporting explains the past. Management Intelligence improves the future.

The platform must therefore do more than display dashboards. It must connect operational facts to business objects, measurements, signals, intelligence, recommendations, management decisions, accountable execution, and learning.

---

## Architectural Principles

### 1. Business meaning before technical convenience

The system must organize data around dealership business objects and management decisions, not around source-system tables or vendor-specific schemas.

### 2. Intelligence must be explainable

Every signal, insight, recommendation, and priority must be traceable to the measurements, rules, comparisons, and business context that produced it.

### 3. One definition for each business concept

Metrics, entities, statuses, and relationships must have canonical definitions. Duplicate calculations and competing meanings are not acceptable.

### 4. Decisions are first-class objects

The platform must persist decisions, owners, commitments, timelines, risks, evidence, follow-up results, and learning. A recommendation that disappears after a meeting has little management value.

### 5. Execution closes the loop

The system must connect decisions to actions and actions to measurable outcomes. Intelligence without execution is merely expensive observation.

### 6. AI supports judgment rather than replacing accountability

AI may summarize, classify, detect patterns, generate recommendations, and surface historical context. Final management decisions remain attributable to human leaders.

### 7. The architecture must scale by domain

Production Intelligence, Execution Intelligence, Financial Intelligence, Customer Intelligence, Workforce Intelligence, and future domains must use shared contracts while retaining domain-specific logic.

### 8. Source systems remain authoritative for source facts

ProdTracker may normalize, interpret, enrich, and connect data, but must preserve lineage back to the originating systems and ingestion events.

---

## Management Intelligence Pipeline

```text
Operational Data
      ↓
Business Objects
      ↓
Measurements
      ↓
Signals
      ↓
Intelligence
      ↓
Recommendations
      ↓
Management Decisions
      ↓
Operational Execution
      ↓
Measured Results
      ↓
Continuous Learning
```

Each stage has a distinct responsibility:

| Stage | Responsibility |
|---|---|
| Operational Data | Capture facts from source systems, user input, and integrations |
| Business Objects | Normalize facts into canonical dealership entities |
| Measurements | Calculate governed KPIs, rates, balances, counts, and variances |
| Signals | Detect material conditions, thresholds, trends, and exceptions |
| Intelligence | Interpret why a condition matters and what may be causing it |
| Recommendations | Propose prioritized actions with expected impact and rationale |
| Management Decisions | Record the chosen action, owner, timing, risk, and commitment |
| Operational Execution | Track work performed against the decision |
| Measured Results | Compare actual outcomes with expected outcomes |
| Continuous Learning | Improve rules, confidence, recommendations, and management memory |

---

## High-Level Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                    Experience Layer                          │
│  Executive | GM | Department | Manager | Journal | Mobile  │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                    Application/API Layer                     │
│  Query | Workflow | Decisions | Actions | Reviews | Alerts  │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                Management Intelligence Layer                 │
│ Measurements | Signals | Intelligence | Recommendations     │
│ Prioritization | Explainability | Learning                  │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                    Business Object Layer                     │
│ Store | Department | RO | Employee | Vehicle | Decision     │
│ Metric | Signal | Action | Commitment | Review | Outcome    │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                  Data and Integration Layer                  │
│ DMS | CRM | OEM | Financial | Survey | Labor | User Input  │
│ Ingestion | Validation | Mapping | Lineage | Event Stream    │
└──────────────────────────────────────────────────────────────┘
```

---

## Layered Architecture

## 1. Experience Layer

The experience layer provides role-based access to Management Intelligence.

Primary experiences include:

- Executive portfolio view
- Market and regional view
- General Manager view
- Department leader view
- Operating review workspace
- Management Decision Journal
- Action and commitment tracking
- Mobile review and notification experience
- AI-assisted meeting and decision review

The experience layer must not contain authoritative business calculations. It presents governed results obtained through application services and intelligence contracts.

### Experience design requirements

- Role-aware scope and permissions
- Consistent metric definitions across pages
- Visible source lineage and freshness
- Clear separation between fact, inference, recommendation, and decision
- Direct navigation from outcome to driver and from driver to underlying evidence
- Minimal dependence on static reports
- Support for review workflows rather than passive dashboard consumption

---

## 2. Application and API Layer

The application layer coordinates user interactions and domain workflows. It exposes stable APIs to the user interfaces, integrations, automation processes, and future clients.

Primary capabilities include:

- Authentication and authorization
- Organization and hierarchy resolution
- Business object queries
- Measurement queries
- Intelligence retrieval
- Recommendation acceptance, rejection, or modification
- Decision creation and revision
- Action assignment and completion
- Operating review creation and facilitation
- Journal entry management
- Notification and alert delivery
- Audit history retrieval

### API design

APIs should be organized around business capabilities, not database tables.

Examples:

```text
GET  /stores/{storeId}/operating-review
GET  /stores/{storeId}/intelligence/production
GET  /stores/{storeId}/measurements
POST /decisions
POST /decisions/{decisionId}/actions
POST /recommendations/{recommendationId}/accept
POST /recommendations/{recommendationId}/reject
GET  /reviews/{reviewId}/commitments
```

Versioning must protect consumers from breaking changes. Domain contracts should use explicit schema versions and effective dates.

---

## 3. Business Object Layer

The Business Object Layer is the canonical semantic model of the platform. It separates dealership meaning from the structure of source systems.

Representative objects include:

- Organization
- Market
- Store
- Department
- Team
- Employee
- Technician
- Advisor
- Customer
- Vehicle
- Repair Order
- Repair Order Line
- Labor Operation
- Inspection
- Recommendation
- Estimate
- Sale
- Appointment
- Task
- Metric Definition
- Measurement
- Target
- Benchmark
- Signal
- Intelligence Finding
- Recommendation
- Decision
- Action
- Commitment
- Risk
- Operating Review
- Journal Entry
- Outcome
- Learning Record

The canonical definitions and relationships are governed by:

- `Business-Object-Model.md`
- `Object-Relationships.md`
- Domain specifications
- Common measurement definitions
- Intelligence contracts

Source-specific identifiers must be retained as external references but must not become the primary semantic identity of a business object.

---

## 4. Measurement Layer

The Measurement Layer calculates governed business measurements from normalized objects and source facts.

A measurement must include at minimum:

- Metric definition identifier
- Subject and organizational scope
- Time period
- Value
- Unit
- Calculation version
- Source lineage
- Data freshness timestamp
- Completeness status
- Confidence or quality status when applicable

Examples include:

- Customer-pay gross profit per repair order
- Hours per repair order
- Effective labor rate
- Technician efficiency
- Repair order cycle time
- Video creation rate
- Video view rate
- Task completion under one hour
- Controllable opportunity count
- Conversion rate
- Customer satisfaction variance to benchmark
- Budget pace
- Year-over-year variance
- Technician Sustainability Index
- Utilization Variance Index

Calculations must be centralized and reusable. User interfaces, exports, and domain engines must not independently recreate metric logic.

---

## 5. Signal Layer

Signals identify business conditions that deserve attention.

A signal is not yet a management conclusion. It is a structured observation such as:

- Metric below target
- Trend deteriorating
- Variance outside expected range
- Dependency concentration rising
- Opportunity volume materially exceeding conversion
- Completed work remaining unclosed
- Customer satisfaction declining despite financial improvement
- Execution behavior inconsistent with stated priorities

Signals may be produced by:

- Static thresholds
- Comparative rules
- Trend analysis
- Statistical anomaly detection
- Correlation patterns
- Domain-specific models
- AI-assisted classification

Every signal must identify:

- Triggering measurements
- Rule or model version
- Severity
- Confidence
- Time window
- Scope
- Expiration or resolution condition

---

## 6. Intelligence Layer

The Intelligence Layer interprets signals in business context.

It answers questions such as:

- What changed?
- Why does it matter?
- What appears to be driving it?
- Is the issue structural, temporary, or execution-related?
- What other business objects are affected?
- What management constraint is most likely limiting performance?
- What evidence supports the conclusion?

Initial intelligence domains include:

- Production Intelligence
- Execution Intelligence

Future domains may include:

- Financial Intelligence
- Customer Intelligence
- Workforce Intelligence
- Capacity Intelligence
- Inventory Intelligence
- Leadership Intelligence
- Risk Intelligence

Each domain consumes shared business objects and measurements and returns outputs through a common Intelligence Contract.

---

## 7. Recommendation Engine

The Recommendation Engine converts intelligence into proposed management actions.

A recommendation must include:

- Recommended action
- Business rationale
- Supporting evidence
- Affected scope
- Priority
- Expected impact
- Expected time to impact
- Required owner role
- Dependencies
- Risks
- Confidence
- Alternatives considered when available
- Expiration or review date

Recommendations may be generated by:

- Deterministic playbooks
- Domain rules
- Historical outcome patterns
- Similar-store comparisons
- AI-assisted reasoning
- Hybrid rule and model approaches

Recommendations must remain distinguishable from decisions. The system proposes; accountable leaders decide.

---

## 8. Decision Layer

The Decision Layer is the center of the Management Decision Platform.

A decision records:

- The condition being addressed
- The selected action
- The leader making the decision
- The accountable owner
- Supporting evidence
- Expected outcome
- Measurement of success
- Start date
- Due date
- Review cadence
- Risks and constraints
- Related recommendations
- Related journal entries
- Related meeting or operating review
- Final outcome
- Learning captured after completion

Decisions may generate one or more actions and commitments. Changes to a decision must be versioned rather than silently overwritten.

The Decision Layer creates an institutional management memory. It allows the platform to answer not only what happened, but also:

- What leaders believed at the time
- What action they chose
- Who owned the commitment
- Whether the expected result occurred
- What pattern should influence future decisions

---

## 9. Workflow and Execution Layer

The Workflow and Execution Layer converts decisions into accountable operating activity.

Core capabilities include:

- Action assignment
- Due dates and recurring cadence
- Status tracking
- Evidence attachment
- Progress updates
- Escalation
- Dependency tracking
- Completion validation
- Outcome measurement
- Follow-up review

Execution states should be explicit and governed, for example:

```text
Proposed → Accepted → Assigned → In Progress → Blocked → Completed → Verified → Closed
```

A completed action is not automatically a successful decision. Verification must compare actual results with the intended outcome.

---

## 10. Data and Integration Layer

The Data and Integration Layer acquires and normalizes operational information.

Potential source categories include:

- Dealer management systems
- Customer relationship management systems
- OEM reporting systems
- Financial statements
- Scheduling systems
- Inspection and video platforms
- Customer survey platforms
- Payroll and workforce systems
- Parts inventory systems
- User-entered observations
- Meeting recordings and transcripts
- Imported spreadsheets and files

### Integration pattern

```text
Source Adapter
    ↓
Raw Ingestion
    ↓
Validation and Quarantine
    ↓
Canonical Mapping
    ↓
Business Object Persistence
    ↓
Measurement and Event Processing
```

### Integration requirements

- Idempotent ingestion
- Source timestamp preservation
- Ingestion timestamp preservation
- Schema versioning
- Duplicate detection
- Validation status
- Error quarantine
- Retry capability
- Reconciliation reporting
- Full lineage

No source should be assumed complete or correct merely because it arrived through an API. Human organizations have already demonstrated that automation can distribute bad data with breathtaking efficiency.

---

## Event Architecture

The platform should use domain events to decouple ingestion, measurement, intelligence, workflow, and notification processes.

Representative events include:

```text
OperationalDataImported
BusinessObjectCreated
BusinessObjectUpdated
MeasurementCalculated
MeasurementRecalculated
SignalDetected
SignalResolved
IntelligenceGenerated
RecommendationCreated
RecommendationAccepted
DecisionRecorded
ActionAssigned
ActionCompleted
OutcomeVerified
LearningCaptured
```

Events should include:

- Event identifier
- Event type
- Schema version
- Aggregate or subject identifier
- Organizational scope
- Occurred timestamp
- Recorded timestamp
- Correlation identifier
- Causation identifier
- Actor or system source
- Payload reference

Event delivery should support retries, dead-letter handling, deduplication, and observability.

---

## Data Architecture

The platform may use multiple persistence patterns, each selected for a specific responsibility.

### Transactional store

Used for:

- Business objects
- Decisions
- Actions
- Commitments
- Reviews
- Permissions
- Workflow state

### Analytical store

Used for:

- Historical measurements
- Trends
- Comparative analysis
- Aggregations
- Domain model features
- Portfolio analysis

### Object storage

Used for:

- Imported files
- Attachments
- Meeting recordings
- Transcripts
- Generated reports
- Evidence artifacts

### Search or retrieval index

Used for:

- Journal entries
- Decision history
- Meeting content
- Recommendations
- Policies and playbooks
- Semantic retrieval for AI workflows

### Cache

Used for:

- Frequently accessed measurement sets
- Role and hierarchy resolution
- Dashboard summaries
- Intelligence snapshots

The system of record for each object type must be explicitly documented. Derived stores may improve performance but must not silently become competing authorities.

---

## AI Architecture

AI is a capability within the architecture, not a substitute for the architecture.

### Supported AI use cases

- Meeting transcription and summarization
- Decision and commitment extraction
- Classification of management concerns
- Pattern recognition across reviews
- Explanation generation
- Recommendation drafting
- Historical context retrieval
- Natural-language querying
- Risk and inconsistency detection
- Management journal synthesis

### AI processing pattern

```text
Governed Context
      ↓
Prompt and Policy Assembly
      ↓
Model Invocation
      ↓
Structured Output Validation
      ↓
Evidence and Citation Binding
      ↓
Human Review or Automated Rule Gate
      ↓
Persisted Intelligence Artifact
```

### AI guardrails

- Structured schemas for model outputs
- Source evidence attached to claims
- Separation of fact, inference, and recommendation
- Confidence indication
- Prompt and model version tracking
- No autonomous high-impact decision execution
- Human confirmation for management decisions
- Tenant and organizational data isolation
- Sensitive-data filtering
- Evaluation against known outcomes

The platform should retain the conversation layer from meetings and the decision layer from the Management Decision Journal, but should not confuse the two. A transcript records discussion. A decision object records accountability.

---

## Security Architecture

Security must be enforced across organizational, functional, and data boundaries.

### Core controls

- Strong authentication
- Role-based and attribute-based authorization
- Organization and store scoping
- Least-privilege service access
- Encryption in transit and at rest
- Secret management
- Audit logging
- Data retention policies
- Sensitive-data classification
- Administrative action review
- Environment isolation
- Dependency and vulnerability management

### Authorization examples

- Executives may view portfolio-level results
- Market leaders may view assigned markets and stores
- General Managers may view their store and authorized comparisons
- Department leaders may view their department scope
- Individual employees may view only explicitly authorized personal information
- AI services may access only the context required for the active request

Authorization must be applied in the service and data-access layers, not merely hidden in the interface like a key left under the doormat.

---

## Explainability and Auditability

Every intelligence artifact must be reconstructable.

The system should be able to answer:

- Which source facts were used?
- Which metric definitions were applied?
- Which rule or model produced the signal?
- Which prompt and model version produced AI content?
- Which evidence supported the recommendation?
- Who accepted, rejected, or modified it?
- What decision was made?
- What result followed?

Audit records must be immutable and time-stamped. Recalculations should create new versions or preserve prior values where material to historical decisions.

---

## Observability

The platform must expose the health of both technical processing and business intelligence.

### Technical observability

- Ingestion latency
- Integration failures
- Queue depth
- Event processing failures
- API latency and error rate
- Database performance
- AI invocation latency and failure rate
- Cost by service and domain

### Intelligence observability

- Measurement freshness
- Missing-data rate
- Signal volume
- False-positive and false-negative review
- Recommendation acceptance rate
- Recommendation modification rate
- Decision completion rate
- Outcome verification rate
- Expected versus actual impact
- Model and rule drift

---

## Performance and Scalability

The architecture must support growth across:

- More stores
- More markets and organizations
- More source systems
- More intelligence domains
- Longer history
- More frequent data refresh
- More users
- More decisions and journal content

### Scalability approach

- Stateless application services where practical
- Asynchronous processing for ingestion and intelligence generation
- Partitioning by tenant, organization, and time where appropriate
- Incremental measurement recalculation
- Materialized analytical views
- Caching of high-demand summaries
- Independent scaling of ingestion, intelligence, AI, and user-facing services

The design should favor a modular monolith or carefully bounded service architecture until operational scale justifies additional distributed complexity. Microservices are not a maturity badge. They are often merely a more expensive way to lose track of one's own code.

---

## Deployment Architecture

The deployment model should support at least:

- Local development
- Automated test environment
- Staging environment
- Production environment

### Deployment requirements

- Infrastructure as code
- Automated database migrations
- Automated tests
- Security scanning
- Versioned releases
- Feature flags
- Rollback capability
- Environment-specific configuration
- Backup and recovery testing
- Health checks
- Release audit trail

The `v40526` production beta branch remains protected. Management Intelligence v5 development occurs on `mi-v5` until release criteria are satisfied.

---

## Domain Extension Pattern

Each new intelligence domain should provide:

1. Domain purpose and management questions
2. Required business objects
3. Required measurements
4. Signal definitions
5. Intelligence interpretation rules
6. Recommendation playbooks
7. Expected outcomes
8. Intelligence Contract implementation
9. Explainability requirements
10. Evaluation and learning criteria

A new domain should reuse shared platform capabilities rather than recreate ingestion, identity, measurement, recommendation, workflow, or audit services.

---

## Initial Logical Components

```text
apps/
  web/
  api/

modules/
  identity/
  organizations/
  business-objects/
  measurements/
  signals/
  intelligence/
  recommendations/
  decisions/
  actions/
  operating-reviews/
  journal/
  notifications/
  integrations/
  audit/

intelligence-domains/
  production/
  execution/

platform/
  events/
  persistence/
  ai/
  security/
  observability/
```

This is a logical structure, not a mandate for immediate physical service separation.

---

## Architectural Decision Boundaries

The following decisions must be governed through Architecture Decision Records:

- Canonical identity strategy
- Tenant and organization isolation model
- Transactional database selection
- Analytical storage strategy
- Event transport
- Measurement execution framework
- AI provider and routing strategy
- Search and semantic retrieval approach
- Audit implementation
- Deployment platform
- Data retention and deletion policy
- Integration credential model

Architecture Decision Records should capture context, options, decision, consequences, and future review triggers.

---

## Release Criteria for the Architecture

The architecture is ready to support implementation when:

- Canonical business objects are approved
- Object relationships are approved
- Common measurements are governed
- Intelligence Contracts are defined
- Production and Execution Intelligence conform to the shared contracts
- Decision and action workflows have explicit states
- Security boundaries are documented
- Data lineage is implemented
- Explainability is testable
- Deployment and rollback paths are verified
- The production beta branch remains isolated from incomplete MI v5 work

---

## Summary

Management Intelligence v5 is not a dashboard feature layered over existing reports. It is a decision architecture.

The platform must preserve a continuous chain from operational fact to business meaning, from business meaning to intelligence, from intelligence to management decision, and from decision to verified result.

The architecture succeeds when leaders can consistently answer five questions:

1. What is happening?
2. Why is it happening?
3. What matters most?
4. What decision are we making?
5. Did the decision improve the result?

That closed loop is the technical foundation of the ProdTracker Management Decision Platform.
