Session 019 — Domain 7: Sales / Opportunity Conversion Intelligence

Date: 2026-08-15
Status: FROZEN / PASS
Primary Objective: Define and smoke-test the canonical Management Intelligence™ architecture for legitimate service opportunity, discovery, presentation, conversion, recovery, and financial translation while preserving tenant neutrality and minimizing management data-entry burden.

1. Session Outcome

Domain 7 is frozen.

The session established a tenant-neutral service-opportunity reasoning architecture that allows MI to determine where legitimate opportunity is being created, missed, presented, authorized, completed, deferred, or lost without reducing the management experience to another dashboard.

MI does not determine what the dealership should value. The tenant establishes desired outcomes and operating standards. MI uses evidence to determine what is influencing those outcomes, identifies the earliest material controllable constraint, and directs management attention toward the actions most likely to improve the result.

AutoNation or any other dealer group may later receive a Tenant Intelligence layer using its own terminology, objectives, standards, data, scorecards, and processes. That layer maps onto MI; it does not redefine the canonical foundation.

2. Canonical Opportunity Object

A service opportunity is a legitimate vehicle or customer need supported by evidence and capable of resulting in appropriate recommended work.

MI reasons at the individual Opportunity level. A VIN or repair order may contain multiple opportunities with different dispositions.

Opportunity bases include:

customer request or concern;

due maintenance;

previously deferred work;

walk-around finding;

MPI or physical inspection;

measurement or test;

diagnosis;

vehicle condition;

OEM or vehicle-derived requirement;

tenant-configured maintenance or operating policy.

Legitimate is intentional. MI must never encourage unnecessary recommendations merely to improve a metric.

3. Known and Discovered Opportunity Paths

Known / Write-Up Opportunity

Opportunity known or reasonably available before technician discovery:

customer-requested work;

maintenance due;

prior deferred work;

recalls/OEM requirements;

walk-around findings.

Discovered Opportunity

Opportunity established during the service event:

MPI;

measurement;

battery or other testing;

diagnosis;

tire/brake/mechanical condition;

other credible inspection evidence.

Both paths converge into the same canonical lifecycle.

4. Frozen Opportunity Lifecycle

Opportunity Basis → Eligibility → Evaluation/Validation → Actionable Need Identified → Estimate/Recommendation Created → Presented → Customer Decision → Authorization → Completion → QA/Delivery → Outcome

Category-specific branches may include:

pre-evaluation diagnostic authorization;

write-up maintenance review;

alignment offer before measurement;

decline or deferral;

no decision / unable to contact;

re-presentation;

recovery at a future service event.

Identified, Estimated, Presented, Authorized, and Completed are separate states.

5. Evaluation Principle

MI measures not only what was found and sold, but what reasonably should have been evaluated and was not.

Core concepts:

Eligible Population

Evaluated Population

Non-Evaluated Population

Evaluation Rate

Non-Evaluation Rate

Non-Evaluated should be available as count and rate.

You cannot reliably discover what you do not evaluate.

MI treats a material Evaluation Gap as an upstream constraint before diagnosing downstream discovery or conversion.

Evaluation may mean physical inspection, measurement, testing, diagnosis, maintenance review, or vehicle/OEM data validation.

6. Category Pressure Tests

The lifecycle was tested against Tires, Brakes, Batteries, Alignments, Maintenance, and General Mechanical.

Tires

MI understands eligible/evaluated VINs, condition evidence, actionable findings, Tire VIN Pen as an outcome, one-tire VIN rate as an investigation signal, and Average Tires per Tire-Sale VIN as a core capture measure. One-tire sales are not automatically failures.

Brakes

MI supports condition and axle-level opportunity where evidence permits. Front/rear/both-axle capture must remain condition-supported.

Batteries

Canonical architecture does not require universal Green/Yellow/Red. Source classifications map through:

Condition Evidence → Condition Classification → Actionability

Alignments

Eligibility is tenant configurable. Guided setup may use annual or roughly 12,000–15,000 miles plus condition/event triggers, but the tenant controls the operative rule.

Maintenance

A broad 10,000-mile cadence may be used as a reasonableness signal, while actual due status follows OEM/vehicle/key-read, time/mileage, history, and tenant-specific rules. OE and tenant recommendations remain distinguishable.

General Mechanical

Typical path:

Concern/Symptom → Diagnostic Authorization where required → Diagnosis → Cause/Repair Need → Estimate → Presentation → Decision → Completion

Result: PASS. The canonical model survived all six categories without category-specific redesign.

7. Maintenance Rule Governance

MI should support a Maintenance Rules Library containing Make, Model, Model Year, Powertrain, Mileage/Time Interval, Maintenance Item, Rule Type, Source, Effective Date, Last Verified, Confidence, and Approval Status.

Implementation progression:

V1: Tenant/brand administrator validates or enters rules once; stores inherit them.
V2: MI researches authoritative information and proposes changes for approval.
V3: Where reliable authoritative integrations exist, MI maintains rules and surfaces exceptions/conflicts/material changes.

Automated OE research is planned capability, not a v1 dependency.

8. Tenant-Neutral Architecture

Automotive Reality → Canonical MI Model → Tenant Configuration → Store Operation

Canonical Layer

Universal dealership concepts and relationships.

Tenant Configuration

Tenant-selected objectives, terminology, standards, rules, assumptions, priorities, and management practices.

Tenant Mapping

Translation between source/tenant/OEM/vendor language and canonical MI concepts.

Tenant Intelligence

Organization-specific intelligence built on MI.

If removing a tenant-specific term causes a concept to collapse, the concept is probably not canonical.

9. Guided Configuration

Tenant-configurable must not mean tenant-left-alone.

MI provides:

recommended starting point;

typical operating context/range;

explanation of the intelligence/business effect;

tenant selection and final authority.

MI may later recommend configuration review from sufficient tenant evidence, but it must not silently rewrite governed settings.

10. Desired Outcomes and Benchmarks

MI does not set the tenant's business target.

Desired Outcome: result the tenant chooses to manage toward, potentially derived from budget, forecast, YoY, OEM objective, internal objective, benchmark, trend, or another priority.

Benchmark: comparative reference. It is not automatically a target.

MI Opportunity Estimate: evidence-supported estimate of additional performance potentially available by correcting a material constraint.

11. Opportunity Gap Intelligence

Potential leakage:

Evaluation Gap — eligible opportunity not evaluated.

Discovery Gap — actionable need appears materially under-discovered.

Estimate Gap — identified need did not become an estimate/recommendation.

Presentation Gap — estimate/recommendation did not reach the customer.

Conversion Gap — presented opportunity is not authorizing as expected/configured.

Completion Gap — authorized work was not completed.

Recovery Gap — valid deferred opportunity was not appropriately revisited.

MI should identify the earliest material controllable constraint, not dump every calculable gap on management.

12. Conversion Architecture

Actual Opportunity Conversion Rate

Authorized Legitimate Opportunities ÷ Legitimate Presented Opportunities

A general 25%–50% range is useful guided-setup context. Tenant interpretation is configurable.

Missed Opportunity Capture Assumption

Separate from actual conversion. This is the tenant-configurable factor applied to estimated legitimate missed opportunity to estimate recoverable sales.

MI guided starting reference: approximately 30%.

Tenant-configurable scenarios may include:

25% — Conservative

50% — Aggressive

75% — Aspirational

Example:

200 Non-Evaluated VINs × 18% evidence-supported actionable rate = ~36 estimated missed opportunities.

36 × 30% capture assumption = ~11 potential additional authorizations.

Observed, calculated, inferred, and configured values retain evidence lineage.

13. ODI — Opportunity Discovery Intelligence

ODI is retained as Opportunity Discovery Intelligence, not a simplistic visible score.

An MI-derived assessment of whether legitimate actionable opportunities are being discovered at a rate reasonably supported by the evaluated vehicle population and available evidence.

Evidence may include condition measurements, classifications, vehicle age/mileage, prior history, work mix, technician patterns, service type, store history, comparable populations, and tenant/brand context.

MI distinguishes:

insufficient evaluation;

healthy evaluation with plausible discovery;

healthy evaluation with materially abnormal discovery.

A Discovery Gap is an inference and requires confidence/corroboration.

ODI must never encourage “finding more work” merely because a benchmark exists.

14. Technician Discovery Intelligence

Discovery should be analyzed at the point where opportunity is created, not only where the sale is recorded.

MI should internally determine who is finding what.

Technician Discovery Profile may consider eligible/evaluated population, category findings, severity/actionability, work mix, vehicle population, capability, service type, prior history, and comparable technician behavior.

Manager-facing output stays simple:

Tire Inspection Opportunity — Timmy is finding materially fewer legitimate tire opportunities than technicians evaluating comparable vehicles. His brake and battery discovery are consistent. Review Timmy's tire measurement/inspection process.

The analysis stays in MI; supporting evidence is available on demand.

15. Technician Dependency

Domain 7 expands dependency beyond production:

Production Dependency — who produces FRH.

Capability Dependency — who can perform the work.

Discovery Dependency — who creates legitimate opportunity feeding downstream work.

MI should determine whether dependency is appropriate because of capability or is being created by weak process, training, work mix, or dispatch.

This connects Domain 7 to Capability Envelope, technician classification, proficiency, work mix, UVI, and TSI.

16. Presentation Intelligence

MI reasons separately across:

Need Identified → Estimate Created → Presented → Customer Decision

Evidence may include estimate creation, timestamps, advisor ownership, contact evidence, video creation/viewing, presentation timing, price/value, and final disposition.

Video is supporting evidence, not the sale.

MI may identify:

identified but not estimated;

estimated but not presented;

delayed presentation;

evidence/video patterns associated with materially different outcomes.

17. OCI — Opportunity Conversion Intelligence

OCI is retained as Opportunity Conversion Intelligence.

An MI reasoning capability that analyzes how effectively legitimate presented opportunities become authorized work and identifies material patterns that may explain conversion performance.

OCI may consider category, opportunity basis, advisor, price/value, evidence/video, presentation timing, customer history, deferred history, brand/store patterns, and comparable opportunities.

Managers receive conclusions and useful evidence, not an arbitrary score unless a future use case warrants one.

18. Deferred Opportunity Recovery

A legitimate unresolved need can persist across service events.

MI retains vehicle, opportunity, evidence, date identified, severity/actionability, last presentation, disposition, follow-up eligibility, and relationship to prior opportunity.

Possible dispositions include declined, deferred, unable to contact, time constraint, part unavailable, capacity unavailable, and customer left before decision.

Deferred opportunity must have validity rules and can be completed, superseded, invalidated, or expired.

The ASM should receive relevant current recovery actions, not a giant declined-work report.

19. Financial Translation

Observed Operational Gap → Estimated Legitimate Missed Opportunity → Tenant Capture Assumption → Estimated Recoverable Work → Economic Impact

Economic impact may include FRH, labor sales, parts sales, labor GP, parts GP, and total GP.

Use actual tenant/store/category economics when sufficient evidence exists.

Avoid false precision. Confidence reflects evidence quality and sample size.

20. Opportunity Lineage / No Double Counting

MI must maintain opportunity lineage through the lifecycle so overlapping upstream and downstream gaps are not counted multiple times when estimating recoverable operational or financial opportunity.

21. Materiality and Management Attention

Materiality: whether a condition is consequential enough to justify management attention relative to other risks/opportunities.

MI should prioritize the smallest number of evidence-supported actions with the greatest reasonable ability to improve the tenant's desired outcome.

Conceptual prioritization considers potential impact, evidence confidence, controllability, time to impact, and management effort.

22. Relevant & Valuable Display Principle

MI should present information only when it materially helps the intended management role understand a condition, evaluate evidence, make a decision, or execute an action. The display should contain the minimum information necessary for that purpose, with deeper evidence available on demand.

MI performs the analysis. Displays communicate the intelligence necessary for management.

Role altitude:

GM: material store condition, economic consequence, management focus.

FOD: cross-store/domain constraint and management-action concentration.

SM: specific operating/process/people actions with evidence.

PM: fulfillment/inventory actions and affected parts/work.

ASM: actionable workflow items relevant to current customers/ROs.

The more sophisticated MI becomes internally, the simpler the management experience should become externally.

23. No Forced Action Principle

MI may determine that no material controllable problem exists.

No material controllable constraint identified.

MI must not manufacture management activity merely to appear useful.

24. Smoke Tests

Smoke Test 1 — Low Tire Sales / Technician Discovery

Evaluation strong; conversion healthy; one technician has materially lower tire discovery than comparable technicians while other categories and work mix are normal.

Correct action: Review that technician's tire inspection/measurement process.

PASS

Smoke Test 2 — Strong Discovery / Weak Presentation

120 actionable brake findings; 116 estimates; only 71 presented; 32 authorized. Conversion among presented opportunities is ~45%.

Correct conclusion: Presentation is the primary constraint, not conversion.

PASS

Smoke Test 3 — Authorized Work Not Completed

Evaluation, discovery, presentation, and conversion healthy. 93 jobs authorized; only 68 completed. Evidence points primarily to parts availability and technician capability/capacity.

Correct conclusion: Sales execution is healthy; hand the constraint to Parts and Technician Capacity intelligence.

PASS

Smoke Test 4 — Below Benchmark / No Material Problem

Tire penetration below comparison, but lower-mileage population and recent tire history explain discovery. Downstream execution is healthy.

Correct conclusion: No material controllable tire constraint identified.

PASS

25. Legacy Service Process Validation

A legacy dealership service-process document reviewed during Session 019 validated the architecture against real fixed-operations flow.

It confirmed:

write-up/customer needs and maintenance can create opportunity before technician inspection;

MPI/diagnosis creates additional discovered opportunity;

technician finding, advisor estimate, customer presentation, authorization, repair, QA, delivery, and follow-up are separate states;

promise/status communication is integral;

declined work should persist for appropriate follow-up;

RO lines, op codes, estimates, timestamps, comments, CCR, MPI, video, and communications are evidence;

Concern → Condition → Cause → Correction is useful mechanical reasoning structure.

26. Glossary Update

The existing Management Intelligence™ Glossary remains the authoritative living semantic artifact.

Session 019 updates it to Version 1.1 with Domain 7 canonical terms, acronym library, and frozen principles.

Every future frozen session should include a glossary review/update.

27. Frozen Domain 7 Principles

Tenant-Neutral Core Principle — tenant establishes desired outcomes; MI identifies what influences them and where management action matters.

Evaluation Principle — MI measures what reasonably should have been evaluated and was not.

Upstream Principle — MI seeks the earliest material controllable condition capable of changing the downstream result.

Discovery-at-Origin Principle — discovery is analyzed where opportunity is created.

Legitimate Opportunity Principle — MI never encourages unnecessary recommendations to improve metrics.

Guided Configuration Principle — MI provides informed guidance while tenant management retains authority.

Opportunity Lineage Principle — MI preserves causal lineage and avoids double counting.

Management Attention Principle — MI surfaces the fewest evidence-supported actions capable of materially improving the desired outcome.

Relevant & Valuable Display Principle — MI performs analysis; displays communicate what the intended role needs to understand, decide, or act.

No Forced Action Principle — MI may conclude no material controllable constraint exists.

28. Exit Criteria

Canonical Opportunity Object

Known and discovered opportunity paths

Opportunity lifecycle

Evaluation / Non-Evaluated

Tires, Brakes, Batteries, Alignments, Maintenance, General Mechanical pressure tests

Maintenance rule governance

Tenant-neutral architecture

Guided configuration

Conversion vs missed-opportunity capture

ODI

Technician discovery/dependency

Presentation intelligence

OCI

Deferred opportunity/recovery

Financial translation and lineage

Relevant & Valuable Display Principle

Four end-to-end smoke tests

Glossary v1.1 update

Domain 7 Status: FROZEN / PASS

29. Next Session

Before beginning the next domain:

confirm the next domain number/name against the project source of truth;

carry forward tenant-neutral architecture;

use Evidence Architecture and the Upstream Principle;

minimize manager input and office-bound workflow;

update the Management Intelligence™ Glossary as new canonical terms are frozen.

30. Session Close

Traditional reporting asks:

What did we sell?

Domain 7 enables MI to ask:

What legitimate opportunity existed, was it evaluated, was it discovered, did it become an estimate, did the customer actually receive it, what decision did the customer make, could the operation fulfill the authorization, and what management action is actually worth taking?

The manager should not have to perform that analysis.

MI does the studying. Management manages.