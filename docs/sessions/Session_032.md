# MI v5 Session 032 — Overall Architecture Gate

**Date:** September 13, 2026

**Project:** ProdTracker Management Intelligence™ v5

**Repository:** `ldrobinett/dpo-app.v3.1`

**Branch:** `mi-v5`

**Status:** **COMPLETE / ARCHITECTURE FROZEN**

---

## Session objective

Evaluate the complete ProdTracker V5 Management Intelligence architecture as
one end-to-end management system and determine whether it is coherent,
operationally realistic, scale-neutral, modular, and buildable.

This was a validation exercise, not an architecture expansion session. Frozen
layers remained frozen unless testing exposed either:

1. a genuine canonical contradiction; or
2. an implementation requirement that could not be satisfied within the
   existing model.

The governing question was:

> **Can ProdTracker V5 reliably transform ordinary dealership evidence into
> governed, explainable, actionable Management Intelligence—and learn from the
> outcome—without losing human authority?**

---

## 1. End-to-end architecture

The accepted V5 management loop is:

```text
Source Evidence
    → Ingestion and Evidence Governance
    → Business and Management Intelligence Model
    → Condition Detection
    → Causal Diagnosis
    → Recommendation Selection
    → Reasoning Orchestration
    → Management Position
    → Human Decision
    → Action and Execution
    → Outcome Validation
    → Learning and Adaptation
```

The architecture must consistently answer:

- What business entity, person, role, team, department, store, or market does
  the evidence concern?
- What happened, and during which operating horizon?
- Is the evidence complete, current, reconciled, and sufficiently trustworthy?
- How does Actual compare with validated True Potential?
- What material Condition exists?
- Why is it likely happening?
- What competing explanations were weakened or ruled out?
- What can management influence?
- What intervention is proportionate and feasible?
- Who has the authority and proximity to act?
- What should happen if the diagnosis is correct?
- When should management review the result?
- Did execution occur?
- Did the expected outcome occur?
- What did the outcome teach MI about the diagnosis and intervention?
- Does new evidence justify preserving, weakening, or revising the learned
  relationship?

Human authority remains explicit throughout the loop. MI may detect, diagnose,
recommend, prioritize, challenge assumptions, and learn from outcomes. It does
not silently change governed inputs, rewrite policy, or convert a recommendation
into a management decision.

**Gate 1 — End-to-End Completeness: PASS.**

---

## 2. Canonical consistency

### True Potential and comparative references

- **Validated True Potential** governs attainable operating opportunity.
- **Performance Objective or Budget** records organizational intent or
  commitment.
- **Actual** records realized performance.
- **Forecast** estimates the likely outcome.
- **Prior year, trends, and benchmarks** provide comparative context.

MI may challenge TP as understated, overstated, or stale. It may not silently
alter governed TP inputs.

### Attention and priority

The canonical Condition states are:

```text
NORMAL → OBSERVE → MANAGE → INTERVENE → ESCALATE → CRITICAL
```

Critical / Need / Nice is the management-facing communication layer. Priority
order determines intervention sequence. These models are related but do not
replace one another.

### MVI and confidence

Minimum Viable Intelligence does not lower the truth standard. Limited evidence
may still produce useful MI, but the output must state what is known, inferred,
unknown, and not presently supported.

### The 4P evidence model and intelligence domains

People, Operating Structure/Platform, Process, and Performance organize
available evidence. They do not replace canonical domains, objects, ownership,
or business meaning.

### Learning and governance

Progressive Intelligence may update confidence in learned relationships and
interventions. It cannot autonomously rewrite governed formulas, TP inputs,
policy, authority, canonical definitions, or frozen architecture.

### Management Capacity and Critical Override

Management Capacity limits normal active priorities to a responsibly executable
set. Independently Critical Conditions may override that compression when delay
creates material consequence.

**Gate 2 — Canonical Consistency: PASS.**

---

## 3. Evidence and authority integrity

MI distinguishes among:

1. validated source evidence;
2. governed calculations and inputs;
3. supported inference;
4. causal hypothesis;
5. human narrative; and
6. unknown or insufficient evidence.

A manager's explanation is evidence to test, not an automatic override of
validated mathematics. A calculated result is not authoritative when its source
evidence is stale, incomplete, unreconciled, or incorrectly governed.

Every material conclusion preserves source identity, operating period,
freshness, completeness, reconciliation status, transformation and calculation
lineage, and known limitations.

MI separately preserves:

- evidence authority;
- calculation authority;
- decision authority;
- action ownership;
- oversight responsibility; and
- escalation authority.

Learning remains evidence-based, probabilistic, explainable, reversible,
subject to contradiction and decay, and subordinate to governed policy and
human authority.

**Gate 3 — Evidence and Authority Integrity: PASS.**

---

## 4. Causal and economic integrity

V5 begins with governed economic decomposition:

```text
CP GP
    → RO Volume × CP GP/RO

CP GP/RO
    → Labor GP/RO + Parts GP/RO

Labor GP/RO
    → Hrs/RO × ELR × Labor Margin

Parts GP/RO
    → Hrs/RO × ELR × Parts-to-Labor × Parts Margin
```

This identifies where the economic gap resides. It does not automatically prove
why the gap exists.

MI moves upstream through demand, work content, write-up, discovery,
presentation, authorization, production, and close. People and Operating
Structure/Platform evidence may explain Process and Performance Conditions.

For every material diagnosis, MI evaluates plausible competing explanations and
disconfirming evidence. It preserves uncertainty when evidence cannot reliably
discriminate among hypotheses.

Before aggregating economic opportunity, MI evaluates shared causes,
dependencies, overlap, sequencing, capacity limits, demand limits, and
compounding effects. Apparent opportunities cannot be added beyond governed
attainable capacity merely because several metrics identify adjacent gaps.

Observed outcomes, supported forecasts, estimated opportunities, and untested
counterfactuals remain distinct. Improvement after an intervention does not, by
itself, prove causation.

**Gate 4 — Causal and Economic Integrity: PASS.**

---

## 5. Management reality

A manager needs the answer to:

> **What deserves my attention today, why does it matter, who owns it, what
> should happen next, and when should we review it?**

V5 produces a compressed Management Position rather than an undifferentiated
alert list. It determines:

- which Conditions share an upstream cause;
- which Conditions remain independent;
- where the failure is concentrated;
- whether management already has an intervention underway;
- whether sufficient time has elapsed to judge it;
- whether proposed actions conflict;
- who has the authority and proximity to act; and
- whether a Critical Condition must override normal prioritization.

V5 distinguishes among insufficient staffing or structural support, lack of
authority, unresolved dependencies, incorrect diagnosis, ineffective
intervention, incomplete execution, and accountable non-performance.

Senior visibility does not automatically transfer operating ownership upward.
Deliberate silence is valid intelligence when no additional action is justified.

**Gate 5 — Management Reality: PASS.**

---

## 6. Scale neutrality

The same canonical objects and relationships work for:

- one independent rooftop;
- a dealer group; and
- an enterprise.

At one rooftop, a single person may perform several roles while their authority
and responsibilities remain conceptually distinct.

At group scale, V5 adds organizational scope, cross-store evidence, shared
services, functional dependencies, and authority relationships without changing
the meaning of Conditions, diagnoses, recommendations, commitments, actions, or
outcomes.

At enterprise scale, V5 adds tenant isolation, governed standards, multiple
sources, local configuration, cross-market patterns, and broader oversight.
Scale changes scope, configuration, evidence breadth, and authority routing—not
the meaning of Management Intelligence.

**Gate 6 — Scale Neutrality: PASS.**

---

## 7. Buildability

The architecture can be implemented as bounded components:

- Source ingestion and evidence validation
- Organizational scope and authority
- Evidence Depth Profiles
- Governed metrics and True Potential
- Condition detection
- Causal hypothesis evaluation
- Recommendation selection
- Reasoning orchestration
- Decision, commitment, and execution tracking
- Outcome evaluation
- Management Effectiveness Evaluation
- Scoped learning and pattern transfer
- Tenant capability profiles

The first vertical slice is:

```text
Real dealership evidence
    → Evidence Depth Profile
    → Validated True Potential
    → Material Condition
    → Supported diagnosis
    → Management Position
    → Human decision
    → Action and execution evidence
    → Outcome
    → Local learning
```

Governed calculations and evidence lineage remain explicit. AI may assist with
classification, hypothesis evaluation, explanation, and orchestration without
becoming an untraceable source of business truth.

**Gate 7 — Buildability: PASS.**

---

## 8. Integrated proof

### Scenario A — Independent dealer using DPO and True Potential

The dealer activates technician structure, scheduled hours, DPO governance,
capacity, rates and margins, True Potential, and Actual-versus-potential
comparison.

MI creates an Evidence Depth Profile and recognizes that detailed Process
evidence is unavailable. When performance falls below TP, it identifies the
economic and capacity gap without inventing an unsupported inspection,
presentation, or authorization diagnosis.

The focused product remains useful, truthful, governed, and upgradeable.

**Result: PASS.**

### Scenario B — Dealer group using full MI

MI detects a CP GP/RO gap at one store and:

1. validates source and TP integrity;
2. localizes the gap to one advisor team;
3. identifies a supported presentation-execution hypothesis;
4. treats a similar cross-entity pattern as prior evidence rather than local
   fact;
5. assigns the Service Manager an intervention;
6. establishes an observation horizon;
7. records the manager's commitment;
8. compares reported completion with execution evidence;
9. finds repeated material contradictions between reported and observed
   execution;
10. separates capability, authority, resource, diagnosis, and evidence-integrity
    possibilities;
11. escalates a Management Effectiveness Concern to the GM;
12. preserves the original action owner unless authority is reassigned;
13. measures the outcome and updates local learning; and
14. updates transferable pattern knowledge without exposing tenant data.

**Result: PASS.**

---

## 9. Accepted implementation requirement 1 — Management Effectiveness Evaluation

MI shall evaluate management effectiveness from longitudinal decision,
commitment, verified-execution, outcome, and learning evidence.

The evaluation includes:

- decision quality;
- commitment reliability;
- verified execution;
- follow-through and review discipline;
- outcome quality;
- response to failed interventions;
- learning and adaptation; and
- accuracy of execution reporting.

A manager's completion claim is evidence, not automatic proof. MI compares the
claim with available execution evidence and subsequent operating behavior.

MI may state:

> **Completion was reported, but available evidence does not verify the
> intervention.**

Or:

> **Reported completion conflicts with observed execution evidence.
> Verification is required.**

MI does not claim that a person lied when it can establish only a contradiction.
It distinguishes intent from evidence integrity.

MI also distinguishes among:

- failure to act;
- incomplete or late execution;
- an incorrect diagnosis;
- an ineffective intervention;
- insufficient authority, staffing, time, or resources;
- an external dependency;
- accountable non-performance; and
- repeated failure to learn or adapt.

Persistent or materially contradicted execution patterns may be escalated to
the appropriate oversight authority with evidence, impact, persistence, and
confidence. A single poor outcome does not establish low management capability.

---

## 10. Accepted implementation requirement 2 — Evidence Depth and Scoped Learning

### Evidence Depth Profile

Each entity and operating period has an evidence profile describing:

- **Breadth:** represented 4P domains
- **Granularity:** monthly, daily, RO-level, employee-level, or another supported
  level
- **Historical depth:** available comparable history
- **Frequency:** monthly, daily, intraday, or event-level
- **Freshness:** currency of the evidence
- **Completeness:** presence of expected records and fields
- **Continuity:** material evidence gaps
- **Reliability:** source, reconciliation, and validation quality
- **Scope:** person, team, department, store, market, organization, or tenant

MI uses this profile to determine what depth of reasoning the available evidence
can support. Richer evidence increases diagnostic depth and confidence; it does
not change canonical meaning.

### Scoped learning levels

```text
Entity learning
    → Tenant or cohort learning
    → Cross-tenant pattern learning
```

Entity learning applies to a specific person, team, department, or store.
Tenant or cohort learning operates across authorized comparable entities within
an organization.

Cross-tenant learning uses appropriately protected, aggregated, de-identified
learning artifacts. Raw evidence, identity, proprietary performance, and
management history remain isolated.

A relationship learned elsewhere is prior evidence or a prior hypothesis—not a
fact about the current dealer. Local evidence must validate, weaken, or reject
the transferred hypothesis.

Every learned pattern carries:

- learning scope;
- evidence-depth requirements;
- originating context;
- cohort comparability;
- confidence;
- transferability;
- freshness;
- contradictory evidence; and
- local-validation status.

> **MI may transfer learning without transferring protected evidence or
> assuming that a pattern supported elsewhere is true locally.**

---

## 11. Accepted implementation requirement 3 — Capability Modularity

ProdTracker V5 supports tenant-selectable capability profiles ranging from a
focused operating tool to the complete Management Intelligence system.

The capability progression is:

```text
DPO Management
    → True Potential
    → Performance vs. Potential
    → Condition Detection and Diagnosis
    → Recommendations and Management Workflow
    → Full Orchestration and Learning
```

A focused dealer configuration may activate only:

- technician structure and scheduled hours;
- governed DPO;
- capacity;
- True Potential calculations; and
- Actual-versus-potential visibility.

Each capability profile declares:

- enabled capabilities;
- required inputs;
- optional evidence;
- dependency requirements;
- data-readiness status;
- available outputs;
- intentionally unavailable intelligence; and
- progressive upgrade path.

Selected capability and supported evidence depth remain distinct. A tenant may
select full MI without yet possessing the evidence required for deep Process
diagnosis. A tenant selecting DPO and TP may intentionally exclude broader MI
outputs even when additional evidence is available.

> **A tenant may activate a governed subset of capabilities without creating a
> different canonical product, redefining shared concepts, or requiring a
> separate data model.**

V5 remains one progressively enabled platform—not separate Lite and Full
architectures.

---

## 12. Overall Architecture Gate decision

- End-to-End Completeness: **PASS**
- Canonical Consistency: **PASS**
- Evidence and Authority Integrity: **PASS**
- Causal and Economic Integrity: **PASS**
- Management Reality: **PASS**
- Scale Neutrality: **PASS**
- Buildability: **PASS**
- Integrated Proof: **PASS**

The review identified three accepted implementation requirements:

1. **Management Effectiveness Evaluation**
2. **Evidence Depth and Scoped Learning**
3. **Capability Modularity**, including a focused DPO and True Potential
   configuration

All three requirements fit within the existing canonical objects,
relationships, evidence model, authority model, tenancy boundaries, and
learning architecture. None requires reopening a frozen layer.

---

## 13. Architecture freeze

> **ProdTracker Management Intelligence V5 Architecture**
>
> **Overall Architecture Gate: PASSED**
>
> **Status: FROZEN**
>
> **Freeze date: September 13, 2026**

Changes after freeze require either:

1. a demonstrated canonical contradiction; or
2. an implementation requirement that cannot be satisfied within the existing
   architecture.

The three accepted implementation requirements must be implemented within the
frozen canonical architecture. They do not reopen or redefine it.

Implementation decisions concerning schemas, formulas, thresholds, services,
interfaces, workflows, capability packaging, and deployment belong in build
specifications unless they expose one of the two valid reasons for change.

---

## Architecture status at close

- Domains 1–12: **FROZEN**
- Canonical Object Model: **FROZEN**
- Layer 1 Source and Ingestion: **FROZEN**
- Layer 2 Business and Management Intelligence Model: **FROZEN**
- Layer 3 Management Intelligence Reasoning Engine: **FROZEN**
- Overall ProdTracker Management Intelligence V5 Architecture: **FROZEN**

## Session result

**SESSION 032 — COMPLETE.**

The overall Architecture Gate passed. The complete V5 architecture is frozen as
of September 13, 2026, with Management Effectiveness Evaluation, Evidence Depth
and Scoped Learning, and Capability Modularity accepted as implementation
requirements.

**Restart marker:** Begin the end-to-end vertical slice:

```text
Real ProdTracker Evidence
    → Evidence Depth Profile
    → True Potential
    → Condition
    → Causal Diagnosis
    → Management Position
    → Manager Decision and Action
    → Outcome and Learning
```
