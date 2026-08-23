# MI v5 Session — 2026-08-23

## Milestone
Layer 2 canonical business model is vetted and frozen through **2.10 Goals, True Potential, Forecast & Planning**. Next domain: **2.11 Risk, Exception & Escalation**.

## Session focus
This session advanced the MI v5 canonical architecture from ingestion and continuity through management reasoning, action, learning, cadence, and economic potential.

## Layer 1 decisions reinforced
- Source ingestion must be idempotent and source-aware.
- Alternate-source operation must notify the responsible manager and clearly state what must be done until the primary source returns.
- Continuity Mode must allow the department to continue operating during a prolonged DMS outage.
- Continuity RO supports multiple repair lines, estimates/authorization/signature, customer legal language, labor, parts, supplies, taxes, deductibles, and RO totals.
- Parts must support parts-in/parts-out records tied to RO lines and non-RO invoices such as wholesale/retail.
- Existing WIP may be recreated as Continuity ROs when completed/cashed out during a prolonged outage, with later reconciliation to the restored DMS.
- Future product pin: a MyKarma-like operating/customer workflow system backed by MI Digital FOD, but this is not current scope.

## Layer 2 canonical architecture

### 2.1–2.2 Organization / responsibility
- Canonical organization and role model must survive vacancies, vacations, transfers, and temporary coverage.
- Vacant SM/PM roles require an accountable temporary operator for daily ingestion and actions; unresolved actions route to the GM as appropriate.
- ASM technician teams can be temporarily reassigned during absence and automatically return to their home assignment when the temporary assignment ends.

### 2.3 Demand taxonomy
Canonical demand taxonomy is intentionally simple:
- Competitive
- Maintenance
- Repair

Tenant-specific deeper classifications may exist below CMR without changing the canonical model.

Demand can be recognized at:
- Appointment / initial write-up
- Found at write-up / walk-around
- Inspection discovered

MI should classify demand from appointment/RO text and improve classification from validated use over time. Inspection-discovered is sufficient; separate inspection/diagnostic/technician-discovered categories are unnecessary for the canonical model.

Diagnostic-only visits are materially important because repeated diagnostic-only behavior may indicate customers are taking repair work elsewhere.

Presentation attempts should capture communication method (text, phone, in-person, etc.) rather than merely free-form notes.

### Parts management scope
Normal MI mode should not recreate the DMS. Parts should focus on management-level signals needed for action, including fill rate, SOP, aging buckets, DSO, non-RO/wholesale-retail performance, and related operating conditions. Much of this can operate at weekly rather than intraday frequency where appropriate.

## Financial / operating economics
Canonical CP GP logic:

Service GP/RO = ELR × Hrs/RO × Labor Margin

Parts GP/RO = ELR × Hrs/RO × Parts-to-Labor Ratio × Parts Margin

Total CP GP/RO = Service GP/RO + Parts GP/RO

Expected CP GP = CP GP/RO × CP RO Count

Parts-to-labor ratio and labor/parts margin are first-class economic drivers.

Expense efficiency should generally be evaluated as the applicable semi-fixed expense divided by the applicable departmental gross. NADA should be used as the default/reference standard where authoritative thresholds exist, while tenant standards remain configurable.

Absorption should similarly have a canonical/default basis while allowing tenant configuration.

Warranty lag is recognized, but MI should reinforce Warranty Live Coding so ROs can close as the vehicle leaves whenever operationally possible.

## Technician production definitions
Canonical definitions:
- Productivity = hours working on vehicles / clock hours
- Efficiency = flagged/earned hours / actual hours spent on the job. Example: 2.0-hour job completed in 1.0 actual hour = 200% efficiency.
- Proficiency = flagged hours / clock hours

MI maintains an upstream mindset: identify the 1–3 materially upstream causes rather than merely reporting downstream KPI misses.

## 2.7 Decision, Action & Commitment — FROZEN
Canonical management chain:

Condition → Diagnosis → Recommendation → Decision → Action → Owner → Commitment → Execution → Outcome → Learning

Key principles frozen:
- Single Accountability
- Delegation with accountability lineage
- Action Supersession
- Action Dependency
- Cadence vs repeated independent tasks
- Execution Conflict
- Accountability Fairness
- Proportional Accountability

Actions can be partial, superseded, deferred, or invalidated by changed conditions. Repeated commitments/cadences are not automatically separate tasks. MI tracks enough execution evidence to determine whether the intervention occurred without becoming an employee-surveillance system.

## 2.8 Outcome, Learning & Management Memory — THICK TEST PASSED / FROZEN
Canonical learning loop:

Condition → Diagnosis → Decision → Action → Expected Outcome → Observed Outcome → Difference → Learning

Outcome types may be leading, intermediate, and lagging.

Key principles:
- Prospective Outcome
- Outcome Attribution
- Net Outcome
- Learning Scope
- Learning Freshness
- Learning Refinement
- Practice Evidence
- Evidence Correction
- Intervention Test Validity
- Historical Challenge
- Institutional Knowledge Integrity
- Minimum Necessary Memory
- Decision Quality
- Outcome Durability
- Attribution Uncertainty
- Decision-Learning Separation

MI keeps four dimensions separate:
1. Decision Quality
2. Execution Quality
3. Outcome Quality
4. Learning Confidence

Management Decision Memory preserves:
- Context
- Material condition
- Diagnosis / causal hypothesis
- Decision
- Action / commitment
- Owner
- Expected outcome and horizon
- Observed outcome
- Learning
- Later revision/refinement

Meeting recordings/transcripts are evidence. The Management Decision Journal is the decision layer. Institutional memory should preserve what was learned, not simply everything that was said.

Historical learning principle: MI remembers what worked, what failed, and under what conditions. Historical similarity informs current reasoning according to contextual comparability, evidence quality, recency, execution quality, and outcome durability.

## 2.9 Operating Cadence & Management Events — THICK TEST PASSED / FROZEN
Cadence represents recurring management practice, not merely calendar meetings.

Examples:
- Opening review
- Intraday management checks such as 10/2/4
- End-of-day close
- Weekly review
- MOR
- Parts aging / warranty review

Canonical cadence remains configurable by tenant. 10/2/4 is an implementation, not a universal canonical time standard.

Key principles:
- Operating Calendar Authority
- Operating Day
- Metric Purity
- Calendar Exception
- Local Operating Time
- Temporal Actionability
- Operating Rhythm
- Management Event
- Cadence Effectiveness
- Decision Frequency
- Deliberate Silence
- Persistent Condition
- Alert Suppression
- Role-Relevant Attention
- Management Horizon
- Action Timing Feasibility
- Historical Normality
- Management Information Timing

MI should change reasoning according to the operating horizon. The same metric can mean different things at 9 AM, 2 PM, and close.

Daily asks: What changes today?
Weekly asks: What pattern is emerging?
Monthly/longer-period review asks: What structural decision is required?

Healthy conditions should generally result in deliberate silence or concise confirmation, not manufactured alerts.

## 2.10 Goals, True Potential, Forecast & Planning — THICK TEST PASSED / FROZEN

### Performance Objective
Canonical Performance Objective represents the tenant's governed intended/expected performance level regardless of tenant label such as budget, target, objective, expectation, or goal. A tenant objective is optional; MI can still evaluate True Potential and execution without one.

### True Potential
True Potential is based on the WWS capacity model and should be known at the beginning of the month.

It represents achievable economic production capability under governed operating assumptions, not a theoretical maximum and not the number required to hit a target.

Core monthly model:

Governed operating inputs → WWS Capacity Model → Baseline True Potential → material structural changes → Current True Potential → Forecast → Actual → Potential Realization → Diagnosis/Action/Learning

True Potential includes:
- Technician governed DPO
- Available working days
- Supported demand
- ELR/pricing
- Labor margin
- Parts-to-labor ratio
- Parts margin
- RO-driven parts
- Wholesale/retail non-RO parts
- Applicable backend earnings such as conquest, return management, OE parts bonuses, and tenant-configured programs

Backend programs must retain their real qualification mechanics, including thresholds, tiers, discrete payouts, and eligibility requirements.

### Baseline vs Current True Potential
Baseline True Potential is established and preserved at the beginning of the applicable period.

Current True Potential may change during the month only when material structural evidence changes available capacity, demand, operating time, economics, or supported earning opportunity.

Recoverable execution variance does NOT reduce True Potential. Poor productivity, pricing leakage, weak P/L, or margin leakage remain execution gaps if the governed capability remains reasonably achievable.

### Forecast
Forecast answers: what are we currently likely to produce?

True Potential answers: what is this operation reasonably capable of producing?

Performance Objective answers: what does the tenant expect/want?

Forecast can exceed True Potential; True Potential is not an absolute ceiling. Repeated overperformance becomes evidence for later governed recalibration.

### Potential Realization
Potential Realization Rate = Forecast or Actual / Current True Potential

This allows MI to distinguish:
- above objective but materially below potential
- below objective but realizing nearly all supported potential

This is a key fairness and management distinction.

### Technician DPO governance
The source methodology reviewed today establishes the technician production objective from the higher of the technician's 10-week or 6-month historical FRH production sample, ranks technicians by FRH production into top/middle/bottom thirds, then applies rank-based stretch multipliers:
- Top third: 105%
- Middle third: 110%
- Bottom third: 115%

The resulting DPO is a governed production objective/capability input for the upcoming month and is frozen for that month.

DPO does not change because current-month execution is poor or excellent. Current performance feeds the historical basis for the next period calculation.

DPO is separate from availability:

Frozen DPO × Available Working Days = Current Production Potential

Planned vacation/training should already be reflected in baseline availability. Unexpected absence changes current availability, not DPO.

New technicians without sufficient history require an authorized Provisional DPO methodology until sufficient history exists.

DPO calculations and overrides require lineage: source history, rank, multiplier, calculated value, effective period, authority, and reason for any authorized override.

### Demand constraint
True Potential is realizable capability and therefore considers both production capacity and supported demand.

Realizable Production = min(Available Capacity, Supported Demand)

Supported demand can include appropriately weighted scheduled work, authorized WIP, historically reliable walk-in demand, declined-work recovery, no-show recovery, campaign/recall opportunity, retention/conquest opportunity, and other demonstrated demand channels. Speculative demand should not be treated as guaranteed production.

### Core frozen principles from 2.10
- Performance Objective Principle
- True Potential Principle
- Potential Baseline Principle
- Potential Integrity Principle
- Potential Realization Principle
- Potential Independence Principle
- Demand-Constrained Potential Principle
- Recoverable Variance Principle
- Potential Calibration Principle
- Exceptional Outcome Principle
- Nonlinear Earnings Principle
- Potential Governance Principle
- Potential Non-Ceiling Principle
- Objective Optionality Principle
- Forecast Method / Uncertainty / Integrity principles
- Scenario Feasibility
- Adaptive Planning
- Evidence-Based Recovery
- Decision Baseline

## Product philosophy reinforced
- Scoreboards explain performance; MI exists to improve the future.
- The system should diagnose objectively and provide actionable items rather than generate another report.
- MI should identify the 1–3 materially upstream items management can influence now.
- Historical normality is context, not a standard.
- A correct recommendation delivered after the opportunity has passed has little management value.
- Tenant targets tell MI what management wants; True Potential tells MI what the operation is built to produce; Forecast tells MI what current execution is likely to produce; MI explains the difference and the upstream actions that matter.

## Architecture / storage pin
Future Build Architecture should use layered storage rather than one undifferentiated database:
- canonical relational system of record for business meaning and management history
- raw/durable evidence/object storage
- event/metric history and analytical storage
- semantic/vector retrieval as an index, not source of truth
- hot/warm/cold retention tiers
- source health, mapping, benchmark, learning-confidence, retention, reconciliation, backup and disaster-recovery maintenance

MI requires longitudinal management memory, but raw operational detail should be retained only at the fidelity/duration required for audit, reprocessing, diagnosis, compliance, or learning.

## Vocabulary captured today
- **Canonical** — authoritative/common representation used across implementations.
- **Taxonomy** — organized classification system.
- **Idempotency** — ability to repeat the same operation without creating a different result after the first successful application.
- **Prospective** — looking forward; defined before the future event occurs.
- **Retrospective** — looking backward after an event.
- **Longitudinal** (lon-jih-TOO-dih-nul) — observed across time rather than at a single point.

A separate running vocabulary document should be maintained and updated at the end of future work sessions.

## Next starting point
**2.11 Risk, Exception & Escalation**

Primary question: when does a material Condition become important enough to interrupt normal cadence, and who needs to know or act?

After 2.11, perform a Layer 2 completion/milestone review before moving into the next architectural layer.
