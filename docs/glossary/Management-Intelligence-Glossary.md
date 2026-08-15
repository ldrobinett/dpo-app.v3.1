Management Intelligence™ Glossary

Version: 1.6   Status: Active / Living Document   Created: 2026-07-19  

Purpose

This glossary establishes the canonical language of Management
Intelligence™. Terms defined here should be used consistently across
specifications, ADRs, APIs, user interfaces, tests, and operating
documentation.

Where a term has a broader industry meaning, this document defines its
meaning within the platform.

A

Acceptance Test

A test that verifies a specified business behavior using defined inputs,
conditions, and expected outcomes.

Action

A management or operational step taken in response to an observation,
risk, opportunity, or recommendation.

Actual Production

The completed production credited during a defined period, measured
using the approved source and accounting rules.

Advisor

A service employee responsible for client communication, repair-order
development, presentation of findings, and coordination of authorized
work.

B

Baseline

A defined reference point used to compare current performance, such as
prior year, prior period, budget, target, or peer group.

Business Object

A canonical representation of an entity or concept used across the
platform, such as Store, Technician, Repair Order, Observation, or
Recommendation.

Business Rule

An approved, testable statement that controls how data is interpreted,
calculated, classified, or acted upon.

C

Capacity

The amount of work an operation can reasonably produce during a period
based on available people, skills, time, facilities, equipment, and
constraints.

Confidence

A stated level of certainty attached to an intelligence output based on
evidence quality, completeness, consistency, and model or rule
reliability.

Constraint

A condition that limits execution, production, conversion, timing, or
expected impact.

Controllable Opportunity

An identified opportunity that can be influenced through available
management or operational action.

Core Measurement

A directly observed or explicitly calculated value owned by a domain.

Customer Intelligence

The domain responsible for understanding client behavior, experience,
retention, communication, demand, and related customer outcomes.

D

Daily Operating Standard

A defined behavior or management process expected to occur consistently
during the operating day.

Daily Production Objective (DPO)

The production expectation for a defined period, person, team,
department, or store, based on approved productivity, availability, and
operating assumptions.

Data Freshness

The age of data relative to the time it is expected to be available and
useful.

Data Grain

The level at which data is represented, such as transaction, repair
order, technician-day, store-day, month, or market.

Derived Intelligence

A domain-owned conclusion created by combining measurements, context,
trends, thresholds, business rules, and constraints.

Domain

A bounded area of business knowledge with explicit ownership, rules,
inputs, outputs, and responsibility.

Domain Boundary

The formal line defining what a domain owns, consumes, produces, and
intentionally does not own.

Domain Intelligence

Measurements, observations, risks, opportunities, forecasts, and
explanations produced by a domain from its owned business knowledge.

E

Evidence

The source data, measurements, rules, trends, and context that support
an intelligence conclusion or recommendation.

Execution Intelligence

The domain responsible for evaluating whether approved operating
processes and behaviors are occurring with the expected completion,
timing, quality, and consistency.

Explainability

The ability to trace a material conclusion or recommendation to its
source data, rules, calculations, assumptions, time period, confidence,
and limitations.

Expected Impact

The estimated financial, operational, customer, or organizational result
of addressing a risk or acting on an opportunity.

F

Financial Intelligence

The domain responsible for understanding revenue, gross profit, expense,
budget, trend, mix, margin, absorption, and financial consequence.

Forecast

An estimate of a future condition or result based on current evidence,
assumptions, trends, and known constraints.

Forecast Production

The amount of production expected by the end of a defined period based
on current pace, remaining time, available capacity, and known
constraints.

H

Health Indicator

A domain output that describes whether an operation, process, workforce,
or result is within an acceptable or sustainable range.

Hours Remaining

The amount of productive labor still required or available within a
defined period, depending on the specified context.

I

Intelligence

Contextual, explainable understanding that improves a decision.
Intelligence goes beyond reporting by identifying meaning, risk,
opportunity, likely outcome, or required attention.

Intelligence API

A versioned interface that exposes domain intelligence, recommendations,
explanations, and related platform objects to approved consumers.

Intelligence Domain

See Domain.

Intelligence Output

A domain-produced observation, health indicator, risk, opportunity,
forecast, constraint, or explanation.

K

Key Performance Indicator (KPI)

A measurement selected because it represents progress toward a material
business objective. Not every metric is a KPI, despite humanity's heroic
efforts to label everything important.

L

Learning Engine

The platform component responsible for evaluating outcomes, comparing
predicted and actual impact, identifying patterns, and proposing
governed improvements without silently rewriting approved rules.

M

Management Intelligence™

A governed platform that observes business operations, reasons through
specialized domains, identifies risk and opportunity, explains
conclusions, recommends prioritized actions, and learns from outcomes
while preserving human decision authority.

Measurement

A quantified value derived from observed data according to a defined
rule, unit, grain, and time period.

Metric

A repeatable quantitative measure. A metric becomes a KPI only when it
is tied to a material objective.

Milestone

A defined project capability or outcome with objective deliverables and
exit criteria.

O

Observation

A factual, time-aware statement produced from validated data without yet
prescribing an action.

Opportunity

A supported condition in which feasible action can produce meaningful
improvement.

Opportunity Indicator

A domain-owned signal that identifies realistic, actionable upside and
includes supporting evidence, constraints, and estimated impact.

Organizational Intelligence

The domain responsible for understanding workforce structure, skill,
capacity, sustainability, leadership coverage, dependency, and
organizational risk.

Outcome

The measured result that follows an action or recommendation.

P

Pace

The rate at which a result is being produced relative to elapsed time
and a defined target or comparison.

Production Intelligence

The domain responsible for understanding production objectives, actual
production, pace, recovery, capacity, technician availability, forecast
production, WIP coverage, and hours remaining.

Production Pace

The relationship between actual production and expected production at a
defined point in time.

ProdTracker

The product application evolving into the Management Intelligence™
platform. ProdTracker may remain the product name while Management
Intelligence™ describes the platform architecture and capability.

R

Recommendation

A prioritized, explainable action synthesized by the Recommendation
Engine from domain evidence, risk, opportunity, constraints, expected
impact, urgency, and confidence.

Recommendation Engine

The only platform component authorized to synthesize and issue final
recommendations across one or more intelligence domains.

Recovery

The additional production or execution required, beyond current pace, to
reach a defined objective within the remaining period.

Release

A versioned, validated product state approved for a defined environment
or user group.

Risk

A supported condition that threatens performance, sustainability,
financial results, customer outcomes, or operational reliability.

Risk Indicator

A domain-owned signal that identifies a material threat and includes
trigger logic, severity, evidence, and clear conditions.

S

Session

A numbered work record documenting objectives, decisions, artifacts,
commits, open questions, and next steps. A session records effort; it
does not itself prove completion.

Signal

A meaningful change, pattern, threshold crossing, or condition derived
from one or more measurements.

Source of Truth

The authoritative system, object, or domain responsible for the official
representation of a value or concept.

Store

A dealership operating entity represented within the platform and
bounded by tenant, market, brand, and organizational context.

Sustainability

The ability to maintain required performance over time without
unacceptable dependency, overload, skill imbalance, or organizational
fragility.

T

Target

An approved expected level of performance used to guide operations and
evaluate results.

Technician Availability

The productive time a technician can reasonably contribute during a
defined period after considering schedule, absence, training,
assignment, and known constraints.

Technician Sustainability Index (TSI)

A measure of workforce progression, skill development, knowledge
transfer, mentoring leverage, and pay alignment that indicates whether
technician capability can be sustained and expanded over time.

TSI is not simply retention. It evaluates whether the organization is
developing future capability rather than depending indefinitely on
existing expertise.

Tenant

The highest enforced data-isolation boundary for a customer or
organization using the platform.

Threshold

A governed value used to classify or trigger a condition. Thresholds
require context and should not be treated as universal truth without
review.

Trend

The direction and rate of change observed across a defined sequence of
periods.

U

User Interface (UI)

The presentation and interaction layer through which users consume
intelligence and record actions. The UI is not the authoritative owner
of business logic.

Utilization Variance Index (UVI)

A measure of production concentration and dependency across technicians.
UVI indicates how heavily an operation depends on a small number of
individuals and the risk created when those individuals are absent,
unavailable, retire, or leave.

A high UVI suggests fragile production concentration. A lower, balanced
UVI generally indicates production is distributed more sustainably,
subject to skill mix and business context.

V

Version

A controlled identifier for a document, rule set, contract, model, or
product state.

W

Work in Process (WIP)

Authorized or active work that has not yet been fully completed, posted,
closed, or otherwise resolved according to the applicable operating
definition.

WIP Coverage

The relationship between available work and the production capacity or
objective it is expected to support.

Worked Example

A realistic scenario demonstrating how defined inputs, rules,
calculations, and outputs behave.

Terminology Rules

Use measurement for a quantified value.

Use observation for a factual interpretation of validated data.

Use signal for a meaningful change or condition.

Use risk or opportunity only when evidence and domain rules
support the classification.

Use recommendation only for an output of the Recommendation
Engine.

Use target, budget, forecast, and actual distinctly.

Do not use intelligence as a decorative substitute for
reporting.

Define acronyms on first use in user-facing and architecture
documents.

Additional Canonical Architecture Terms

Actionable Need

A legitimate vehicle or customer need supported by sufficient evidence
to warrant an appropriate recommendation, estimate, presentation,
follow-up, or operational action.

Authorization

A customer decision approving a presented recommendation or estimate.
Authorization is distinct from completion.

Benchmark

A comparative reference used to provide context for performance. A
benchmark does not become a tenant target or desired outcome unless the
tenant explicitly adopts it.

Canonical

A standardized system-level concept used by Management Intelligence™
regardless of terminology used by a specific tenant, OEM, vendor, source
system, or dealership.

Capability Envelope

The range and complexity of work a person, team, or operation can
reasonably perform based on demonstrated skill, training, certification,
experience, equipment, and operating conditions.

Conversion Rate

The percentage of legitimate presented opportunities that result in
customer authorization.

Formula: Authorized Opportunities ÷ Legitimate Presented Opportunities.

A general 25%--50% range may be useful as guided setup context, but
tenant interpretation remains configurable.

Deferred Opportunity

A legitimate actionable need identified but not completed that remains
potentially applicable to a future service event.

Desired Outcome

A business result the tenant has identified as important for management.
It may be based on budget, forecast, year-over-year improvement, OEM
objectives, internal objectives, benchmarks, trends, or other
tenant-selected priorities.

Discovery Gap

An evidence-supported difference between actionable needs actually
identified and the legitimate actionable need MI estimates was
reasonably present within the evaluated population.

Evaluation

The process of appropriately checking, measuring, testing, diagnosing,
reviewing, or validating whether a legitimate need exists.

Evaluation Gap

The eligible population that reasonably should have been evaluated but
was not.

Guided Configuration

A tenant setup process in which MI provides recommended starting values,
operating context, expected consequences, and evidence-based guidance
while preserving tenant authority.

Materiality

The degree to which the magnitude and consequence of a condition justify
management attention relative to other available risks, opportunities,
constraints, and actions.

Missed Opportunity Capture Assumption

A tenant-configurable percentage applied to estimated legitimate
opportunity lost through an identified execution gap to estimate the
portion reasonably recoverable through management action. MI may guide
setup around 30%. Scenario assumptions may be tenant configured,
including 25% Conservative, 50% Aggressive, and 75% Aspirational.

Non-Evaluated

An eligible service event, vehicle, item, or opportunity basis that
reasonably should have received an applicable evaluation but did not.

Ontology

The governed model of canonical concepts and the relationships among
them. A taxonomy organizes classifications; an ontology additionally
describes how concepts relate, interact, depend on one another, and
influence outcomes.

Opportunity Basis

The evidence or operating condition from which a legitimate service
opportunity can originate, including customer request, due maintenance,
deferred work, inspection, diagnosis, vehicle condition, OEM
requirement, or tenant-configured policy.

Opportunity Conversion Intelligence (OCI)

A proprietary MI reasoning capability that analyzes how effectively
legitimate presented opportunities become authorized work and identifies
material patterns that may explain conversion performance. OCI is
intelligence, not merely a visible score.

Opportunity Discovery Intelligence (ODI)

A proprietary MI reasoning capability that assesses whether legitimate
actionable opportunities are being discovered at a rate reasonably
supported by the evaluated vehicle population and available evidence.
ODI is intelligence, not merely a visible score.

Opportunity Gap

A supported point of leakage within the service-opportunity lifecycle
that may represent recoverable operational or financial opportunity.

Opportunity Lineage

The traceable relationship of an opportunity across its lifecycle,
evidence, estimates, presentations, decisions, authorizations,
completion, deferral, recovery, and financial consequence.

Opportunity Lifecycle

The canonical progression used by MI to reason about legitimate service
opportunity:

Opportunity Basis → Eligibility → Evaluation/Validation → Actionable
Need Identified → Estimate/Recommendation Created → Presented → Customer
Decision → Authorization → Completion → QA/Delivery → Outcome.

Opportunity Recovery

The process of appropriately revisiting a legitimate deferred
opportunity while it remains valid and relevant.

Promise at Risk

A service event whose current evidence indicates a material likelihood
that an established customer promise, completion expectation, or
communication commitment will not be met without intervention.

Relevant & Valuable Display

A role-appropriate presentation of intelligence that materially helps
the intended user understand a condition, evaluate evidence, make a
decision, or execute an action. MI performs the analysis; displays
communicate the necessary intelligence.

Taxonomy

A structured classification and hierarchy used to organize related
canonical concepts into defined categories.

Tenant Configuration

The governed objectives, terminology, assumptions, standards, rules,
priorities, and operating practices selected by a tenant and mapped onto
the canonical MI model.

Tenant Intelligence

An organization-specific intelligence layer that maps a tenant's
terminology, objectives, standards, processes, data, and management
practices onto the canonical Management Intelligence™ architecture
without altering the canonical foundation.

Tenant Mapping

The governed translation between tenant, OEM, vendor, or source-system
terminology/data structures and canonical MI concepts.

Technician Discovery Profile

An internal MI intelligence object describing the type, frequency, and
condition distribution of legitimate service opportunities identified by
a technician, normalized where evidence permits for evaluated
population, vehicle/work mix, capability, and relevant context.

Technician Dependency Profile

An internal MI assessment of the degree to which an operation depends on
an individual technician or small group for production, capability, and
legitimate opportunity discovery.

Upstream Principle

MI should look first for the earliest material controllable condition
capable of explaining or changing a downstream result.

Acronym Library

Acronym

Meaning

Classification

Notes

MI

Management Intelligence™

Platform / Canonical

Core reasoning architecture

DPO

Daily Production Objective

Platform / Canonical

Production term

FRH

Flat Rate Hours

Industry

Labor production measure

ELR

Effective Labor Rate

Industry

Effective labor sales rate

DSO

Days Supply on Hand

Industry

Parts inventory supply measurement

MPI

Multi-Point Inspection

Industry / Source-dependent

Inspection process

KPI

Key Performance Indicator

Industry

Metric tied to a material objective

RO

Repair Order

Industry

Core service transaction/document

WIP

Work in Process

Industry

See canonical definition

CP

Customer Pay

Industry

Customer-paid work

WP

Warranty Pay

Industry / Tenant alias

Source terminology may vary

IP

Internal Pay

Industry / Tenant alias

Source terminology may vary

ODI

Opportunity Discovery Intelligence

MI Proprietary

Internal reasoning capability

OCI

Opportunity Conversion Intelligence

MI Proprietary

Internal reasoning capability

TSI

Technician Sustainability Index

MI Proprietary

Workforce sustainability measure

UVI

Utilization Variance Index

MI Proprietary

Production dependency measure

ASR

Additional Service Request

Tenant / Source-dependent

Map to canonical opportunity concepts

OEM

Original Equipment Manufacturer

Industry

Manufacturer/source context

FOD

Fixed Operations Director

Industry / Role

Role terminology varies

SM

Service Manager

Industry / Role

Role terminology varies

PM

Parts Manager

Industry / Role

Role terminology varies

GM

General Manager

Industry / Role

Store executive role

Domain 7 Principles Added

Evaluation Principle: MI measures what reasonably should have been
evaluated and was not.

Discovery-at-Origin Principle: Discovery is analyzed where legitimate
opportunity is created, not only where the sale is recorded.

Opportunity Lineage Principle: MI preserves opportunity lineage so
overlapping gaps are not counted multiple times.

Tenant Intelligence Principle: MI provides canonical reasoning; Tenant
Intelligence maps an organization's terminology, objectives, standards,
processes, data, and practices onto it.

Guided Configuration Principle: MI provides informed setup guidance
while preserving tenant authority.

Relevant & Valuable Display Principle: MI performs analysis; displays
communicate only what the intended role needs to understand, decide, or
act.

Management Attention Principle: MI prioritizes the smallest number of
evidence-supported actions with the greatest reasonable ability to
improve the tenant's desired outcome.

No Forced Action Principle: MI may conclude that no material
controllable constraint exists and recommend no intervention.

Revision History

Version

Date

Change

1.0

2026-07-19

Initial glossary created during Session 009

1.1

2026-08-15

Added Domain 7 opportunity architecture, tenant-neutral terminology,
guided configuration, ODI/OCI, technician discovery/dependency, acronym
library, and display/action principles during Session 019

Revision 1.2

Date: 2026-08-15
Change: Added Domain 8 workforce, capability, coverage, leadership,
succession, intervention effectiveness, MI self-evaluation, MI
Effectiveness Score, quarterly review, and people-evidence architecture
during Session 020.

Domain 9 --- Operating Control, Economic Integrity & Absorption Intelligence Terms

Absorption Driver Analysis

The decomposition of changes in Reported Absorption into supported
gross, expense, leakage, investment, structural, and accounting drivers
and their originating operating causes.

Accounting Recognition

The manner and period in which an Economic Event is recognized within
the tenant's accounting and financial reporting structure.

Capability Dependency

A governed relationship identifying another MI capability or evidence
source required for a capability to function correctly.

Capability Entitlement

The governed right of a tenant to access and use a defined MI capability
based on purchased product, subscription, license, or contracted
configuration.

Canonical Economic Classification

The tenant-neutral economic meaning assigned by MI to an Economic Event
independently from tenant account names, account numbers, or statement
placement.

Digital FOD

The persistent management capability powered by Management Intelligence™
V5 that helps dealership leaders recognize material conditions, make
better decisions, execute appropriate actions, and determine whether
those actions worked. It does not replace dealership management or human
decision authority.

Economic Consequence

The supported financial effect of an operating condition or Economic
Event, including effects on gross, expense, retained contribution,
capacity economics, or absorption.

Economic Event

A business occurrence that creates, transfers, preserves, reduces,
invests, or consumes economic value within the operation.

Economic Leakage

Economic value that was created, available, or reasonably expected but
was not retained because of an operating decision, execution gap,
process failure, quality condition, control deficiency, or preventable
capacity loss.

Economic Lineage

The traceable relationship between a quantified economic consequence and
its originating Economic Event, preserving the ability to analyze the
event through multiple dimensions without double-counting its financial
impact.

Economic Materiality

The significance of an economic condition based on magnitude,
persistence, trajectory, controllability, recurrence, operating
consequence, absorption consequence, confidence, and relevance to
management responsibility.

Evidence-Supported Absorption Opportunity

The improvement in Reported Absorption reasonably supported by currently
identified gross, expense, leakage, capacity, and operating
opportunities.

Financial Mapping Drift

A material change in account usage, transaction composition, posting
behavior, or financial classification that may invalidate or weaken an
existing canonical financial mapping.

Fixed Operations Absorption

The degree to which gross profit generated by fixed operations covers
the dealership operating expense base defined by the tenant's governed
absorption policy.

Management Altitude

The level of condition, evidence, action, and detail appropriate to a
user's organizational authority and management responsibility. Higher
organizational altitude does not automatically imply greater operating
detail.

Price Realization

The degree to which governed or intended selling value is captured in a
completed transaction after discounts, concessions, overrides, and
adjustments.

Reported Absorption

The fixed-operations absorption result produced by the tenant's governed
absorption calculation. MI may explain, decompose, forecast, or model it
but may not silently alter it.

Role Permission

The governed right of an authorized user or role to access a
tenant-entitled MI capability and its permitted level of detail.

Tenant Capability Manifest

The governed source-of-truth configuration identifying a tenant's
purchased and enabled MI capabilities, effective dates, capability
dependencies, evidence status, role permissions, and tenant-specific
extensions.

Tenant Economic Policy

The governed tenant configuration defining financial and economic
treatments used by MI, potentially including absorption definition,
account mappings, expense classifications, capitalization, depreciation,
policy/goodwill, incentives, pricing, sublet, allocations, and
materiality preferences.

Tenant Financial Mapping

The governed relationship translating a tenant financial source or
account into canonical MI economic meaning while preserving tenant
accounting terminology and implementation.

Unapplied Labor

Paid technician labor capacity that was not applied to revenue-producing
or otherwise recognized productive work during the measurement period.

Unapplied Labor Economic Consequence

The supported direct labor cost and/or foregone productive value
associated with unapplied technician capacity, with economic lineage
preserved to prevent double counting.

Domain 9 and Platform Principles Added

Economic Meaning Principle: MI understands the operating
economic meaning of an event independently from where accounting
places it.

Accounting Recognition Principle: MI preserves tenant accounting
treatment while independently understanding the underlying Economic
Event.

Purpose Principle: Increased expense is not inherently negative;
MI distinguishes required cost, productive investment, correction,
structural obligation, and unsupported leakage.

Controllability Principle: MI guidance corresponds to management
authority and a reasonable time horizon for influence.

Economic Leakage Principle: MI identifies preventable failure to
capture or retain reasonably available economic value.

Absorption Integrity Principle: MI never silently adjusts the
tenant's governed Reported Absorption calculation.

Evidence-Supported Absorption Opportunity Principle: MI models
only absorption opportunity supported by identified operating and
economic evidence.

Economic Lineage Principle: Multiple analytical classifications
may reference the same Economic Event without double-counting its
financial consequence.

Economic Consequence Principle: Domain 9 quantifies financial
consequence while corrective ownership remains with the originating
root-cause domain.

Canonical Financial Mapping Principle: Tenant accounting maps
into canonical MI economic meaning rather than defining it.

Historical Integrity Principle: Financial mapping and
accounting-treatment changes are effective-dated and do not silently
rewrite historical interpretation.

Mapping Confidence Principle: MI distinguishes Confirmed,
Inferred, and Unresolved financial mappings.

Mapping Drift Principle: MI evaluates whether financial behavior
remains consistent with governed mappings and surfaces material
drift.

Entitlement Principle: Access to MI capabilities is governed by
purchased tenant entitlement.

Permission Principle: Tenant entitlement and individual role
permission are separate controls.

Evidence Independence Principle: Entitlement status, permission
status, and evidence sufficiency are separate states.

Commercial Neutrality Principle: Canonical MI capabilities
remain independent from commercial packaging.

Digital FOD Continuity Principle: The Digital FOD remains
competent within entitled capabilities without exposing non-entitled
intelligence.

Management Altitude Principle: MI presents the degree of
operating detail appropriate to the user's management
responsibility.

Persistent Management Assistance Principle: The Digital FOD
extends management reasoning, guidance, follow-through, and learning
between direct human leadership interactions.

Revision 1.3

Date: 2026-08-15
Change: Added Domain 9 Operating Control, Economic Integrity &
Absorption Intelligence; canonical economic-event and expense
architecture; accounting recognition; economic leakage; unapplied labor;
price realization; absorption intelligence; tenant financial mapping and
drift; economic lineage; capability entitlement and role permission; and
the platform-level DWP → MI V5 → Digital FOD architecture frozen during
Session 021.

Domain 10 --- Forecasting, Planning & Scenario Intelligence Terms

Action Sequence

The evidence-supported ordering of dependent management interventions
intended to improve the probability that each intervention can produce
its desired effect.

Assumption Provenance

The traceable source, author or derivation, supporting evidence,
confidence, effective period, and change history of a material forecast
or scenario assumption.

Causal Confidence

The degree to which available evidence supports MI's conclusion that one
condition materially contributes to another observed condition.

Dynamic Planning

The continuous reassessment of a management plan as material operating
evidence changes during the planning horizon.

Early Warning Condition

A Leading Condition whose current trajectory indicates material future
risk before the associated Lagging Outcome has materially deteriorated.

Emerging Opportunity

A Leading Condition indicating future performance may exceed current
expectations if management preserves or appropriately acts upon the
developing condition.

Evidence Maturity

The degree to which sufficient historical and current evidence exists to
support reliable future-state reasoning for a particular condition,
metric, store, or model.

External Condition

A sufficiently supported condition originating outside the dealership
operation that may materially influence future operating performance.

Forecast Bias

A persistent tendency for forecast outcomes to systematically exceed or
fall below actual results.

Forecast Calibration

The continuous comparison of prior forecasts against actual outcomes to
determine whether MI's forecasting assumptions, weighting, confidence,
or models require adjustment.

Forecast Confidence

MI's assessment of how strongly available evidence supports a forecast
based on evidence quality, historical stability, known uncertainty,
changing conditions, assumption dependency, and horizon.

Forecast Outcome

The evidence-supported estimate or range of a future result based on
current trajectory, known future conditions, historical behavior, and
explicit assumptions.

Forecast Validity

Whether the assumptions and operating conditions supporting an existing
forecast remain sufficiently intact for the forecast to remain
decision-useful.

Future Mix

The expected composition of future demand, work, customer, labor, parts,
or economic activity where differences in composition materially affect
the forecast.

Horizon Trade-Off

A condition in which an action beneficial within one Management Horizon
creates material adverse consequences in another horizon.

Intervention Fit

The degree to which a proposed management intervention addresses the
evidence-supported root condition responsible for the desired outcome.

Lagging Outcome

A result reflecting the accumulated effect of earlier operating
conditions and decisions.

Leading Condition

An observable operating condition whose change is expected to precede
and materially influence a later operating or economic outcome.

Management Horizon

The period over which an operating condition, forecast, plan, scenario,
or management intervention is intended to remain relevant.

Management Intent

A management-declared future action or desired operating change that may
inform planning but does not become forecast evidence until supported by
execution or other reliable evidence.

Management Pathway

An evidence-supported sequence of operating changes through which
management can reasonably influence a desired outcome.

Management Pattern

A recurring evidence-supported relationship between operating
conditions, management interventions, and observed outcomes.

Objective Conflict

A condition in which actions supporting one desired outcome materially
impair another governed or material outcome.

Operating Trajectory

The evidence-supported direction and rate at which an operating or
economic result is developing if material conditions remain
substantially unchanged.

Operational Foresight

The use of current evidence to identify likely near-term operating
conditions early enough for management or employees to intervene before
the condition becomes an outcome.

Pathway Confidence

The degree to which available evidence supports the expected
relationship between a proposed operating change and the desired
outcome.

Pattern Relevance

The degree to which a historically observed pattern remains supported by
current operating evidence.

Plan Feasibility

The degree to which a management plan can reasonably be executed given
available demand, capacity, capability, time, dependencies, and other
operating constraints.

Plan Sufficiency

The degree to which selected management pathways reasonably address the
magnitude and nature of the identified Planning Gap.

Planning Dependency

A condition that must exist or be sufficiently resolved before another
Management Pathway can reasonably produce its intended effect.

Planning Gap

The difference between a desired outcome and the outcome currently
supported by Operating Trajectory and identified opportunity.

Planning Intelligence

The MI capability that identifies evidence-supported changes in
operating conditions most likely to improve trajectory toward a desired
outcome and helps management select, sequence, and evaluate those
changes.

Planning Priority

The relative management importance of an evidence-supported pathway
based on expected impact, urgency, controllability, confidence,
dependencies, and current operating context.

Root-Cause Compression

The process by which MI reasons upstream across related evidence until
it identifies the smallest defensible set of root conditions capable of
explaining and materially influencing the largest set of relevant
downstream conditions.

Scenario

An evidence-supported representation of a possible future operating
state created by changing one or more explicit assumptions, conditions,
or management decisions.

Scenario Assumption

An explicit condition treated as true for purposes of evaluating a
modeled future state.

Scenario Calibration

The comparison of modeled Scenario outcomes with actual results when the
modeled management change is subsequently implemented.

Scenario Confidence

The degree to which available evidence supports the modeled
relationships and assumptions within a Scenario.

Scenario Constraint

An operating condition that limits the degree to which a modeled
Scenario can produce its expected result.

Scenario Recommendation

The alternative MI believes has the strongest evidence-supported
management case among evaluated scenarios, with reasoning and evidence
lineage preserved.

Scenario Trade-Off

A material positive or negative consequence expected to arise from a
modeled management decision in addition to its primary intended outcome.

Scenario Validity

Whether the evidence and assumptions underlying a previously modeled
Scenario remain sufficiently current for that Scenario to remain
decision-useful.

Seasonal Pattern

A recurring time-dependent variation in operating behavior supported by
sufficient historical evidence.

Second-Order Effect

A downstream operating or economic consequence caused indirectly by the
initial change introduced in a Scenario.

Structural Change Event

A material change in operating structure, leadership, process, capacity,
policy, environment, or business model that may reduce the predictive
relevance of prior historical behavior.

Uncertainty Driver

A condition whose unresolved state materially increases the range or
reduces the confidence of a future-state estimate.

Unexplained Forecast Error

The portion of difference between forecast and actual outcome not
sufficiently explained by known assumptions, evidence changes,
identified disruptions, or supported causal conditions.

Domain 10 Principles Added

Future-State Integrity Principle: Actual results, trajectory,
forecast, plan, and scenario remain distinct concepts and must never
be presented interchangeably.

Root-Cause Compression Principle: MI reasons upstream to
identify the smallest defensible set of root conditions capable of
explaining and materially influencing the largest set of relevant
downstream conditions without forcing artificial simplicity.

Scenario Integrity Principle: Scenarios explicitly state
assumptions and are never presented as forecasts.

Management Authority Principle: MI advises, challenges, models,
and learns; authorized human management retains decision authority.

No Artificial Action Plan Principle: MI does not generate
management actions merely because a metric is below expectation;
recommended actions require an evidence-supported operating
condition and plausible Management Pathway.

Horizon Integrity Principle: MI evaluates management actions
across relevant time horizons and surfaces material conflicts
between short-term benefit and longer-term operating consequence.

One Future-State Model Principle: MI maintains a coherent
future-state model and varies resolution according to role,
responsibility, horizon, materiality, entitlement, and evidence
rather than creating independent versions of the future for each
management level.

Legitimate Outcome Principle: No forecast, plan, scenario,
target, budget, or financial objective may convert unsupported
customer work, unnecessary activity, unsafe behavior, deceptive
practice, or otherwise inappropriate conduct into legitimate
opportunity.

Revision 1.4

Date: 2026-08-15
Change: Added Domain 10 Forecasting, Planning & Scenario
Intelligence; future-state integrity; operating trajectory; forecasting
confidence, validity and calibration; Operational Foresight; Root-Cause
Compression; Planning Intelligence; Management Pathways; plan
sufficiency and feasibility; Scenario Intelligence; management horizons;
seasonality and pattern relevance; evidence maturity; external and
structural conditions; assumption provenance; uncertainty; objective
conflict; and legitimate-outcome protection frozen during Session 022.

Consolidation & Domains 11--12 Canonical Terms

Assumption

An explicit proposition treated as true for a defined reasoning purpose
despite not being established as an observed fact.

Business-First Intelligence Principle

MI begins with the business being managed and scales outward through
organizational context rather than beginning with enterprise hierarchy
and scaling downward.

Business Continuity

The ability of the business to sustain material operating capability,
customer service, leadership function, and economic contribution through
foreseeable personnel, ownership, system, facility, or market change.

Business Value Creation

An evidence-supported condition that materially strengthens sustained
economic performance, operating capability, customer durability,
resilience, continuity, or future flexibility.

Business Value Erosion

A persistent or emerging condition that materially weakens future
economic strength, capability, customer durability, resilience,
continuity, or flexibility.

Condition

An evidence-supported state, pattern, constraint, strength, opportunity,
risk, dependency, or other meaningful operating circumstance inferred or
directly established from Evidence.

Decision

A governed management choice to act, not act, allocate resources, accept
risk, select an alternative, establish direction, or otherwise influence
the business.

Decision Authority Principle

MI may identify, evaluate, recommend, and learn from management
alternatives, but a management Decision becomes authoritative only
through an appropriately authorized human or governed external decision
process.

Decision Quality

The degree to which a management decision was reasonably supported by
the evidence, alternatives, assumptions, risks, and trade-offs available
at the time it was made.

Declared Strategic Intent

A tenant-authorized statement describing a meaningful future direction,
capability, condition, or business characteristic management intends to
create, strengthen, protect, change, or exit.

Entity

An identifiable business, organizational, operational, human, customer,
asset, transaction, or other object about which MI can hold governed
evidence and reason.

Epistemic Status

A governed description of the knowledge status of an object, distinct
from Confidence. Applicable statuses may include Recorded, Corroborated,
Contested, Unverified, Superseded, Invalidated, and Inferred.

Event

An occurrence at a defined point or interval in time that may create,
alter, resolve, or materially contextualize one or more Entities,
Relationships, Conditions, Outcomes, or reasoning states.

External Strategic Evidence

Evidence originating outside the tenant's operating systems that
materially informs a strategic question and retains source, recency,
confidence, applicability, and governance lineage.

Historical Integrity Principle

Canonical MI objects that materially contributed to prior reasoning,
decisions, interventions, or outcomes retain their historical state and
lineage when subsequently corrected, superseded, invalidated, or
reinterpreted.

Intelligence Object

A governed, evidence-linked management conclusion produced by MI that
explains a material condition, relationship, implication, opportunity,
risk, pathway, forecast, recommendation, or decision-relevant insight.

Intervention

A specific management action taken to alter an evidence-supported
Condition or influence an Outcome.

Intervention Restraint Principle

MI recognizes when preserving a functioning condition is more valuable
than unnecessary management intervention.

Management Judgment

A management-provided interpretation, expectation, or decision informed
partly by experience, context, or knowledge not fully represented in
MI's current evidence model. Canonically represented as Declared
Evidence where appropriate.

No-Action Decision

An evidence-supported management Decision to preserve the current
operating state because available alternatives do not presently offer
sufficient expected benefit, confidence, urgency, or strategic value to
justify intervention.

One Object Model, Multiple Intelligence Domains Principle

MI domains apply specialized reasoning to shared canonical Entities,
Relationships, Events, Evidence, Conditions, Outcomes, Assumptions,
Decisions, Interventions, Patterns, and Intelligence Objects. Domains do
not maintain separate versions of business reality.

Operational Wisdom

A mature evidence-supported Pattern whose persistence, replication,
applicability, relevance, and known boundaries are sufficiently
established to improve future MI reasoning and management guidance.

Outcome Quality

The degree to which the eventual observed result was favorable relative
to intended objectives and material consequences.

Pattern

A recurring evidence-supported relationship among Entities, Events,
Conditions, Decisions, Interventions, or Outcomes observed across time
or context and retained because it may improve future reasoning.

Provenance Class

The governed origin class of an applicable canonical object.

Canonical provenance classes: - Observed: recorded by an
authoritative or governed source; - Declared: explicitly provided by
an authorized human or tenant; - Derived: produced deterministically
from governed inputs; - Inferred: produced through MI reasoning.

Relationship

A governed, potentially effective-dated connection between two or more
Entities that gives evidence organizational, operational, causal,
ownership, responsibility, or contextual meaning.

Responsible Management Role

The role possessing meaningful responsibility, authority, or
accountability for the condition or decision under consideration within
the tenant's actual organizational structure.

Scale Neutrality Principle

Canonical MI intelligence remains useful without requiring a particular
organizational size, hierarchy, management layer, or operating
structure. Intelligence scales upward through organizational context
rather than assuming enterprise complexity as the default.

Strategic Alignment

The degree to which material operating decisions, investments,
interventions, capabilities, and observed outcomes support the
business's Declared Strategic Intent.

Strategic Condition

A persistent or emerging condition capable of materially affecting
sustained economic performance, operating capability, customer
durability, resilience, continuity, or future choices of the business.

Strategic Dependency

A business or organizational dependency whose concentration, importance,
or failure consequence is sufficiently material to threaten sustained
performance, continuity, or resilience.

Strategic Materiality

The degree to which a condition matters to sustained business value,
risk, capability, customer durability, resilience, continuity,
governance, or future direction, regardless of immediate financial
magnitude.

Strategic Opportunity

An evidence-supported condition in which structural change, investment,
resource reallocation, capability development, or management-system
improvement could materially strengthen sustained business performance.

Strategic Optionality

The degree to which a decision preserves or creates valuable future
choices, flexibility, capability, or pathways under uncertain future
conditions.

Strategic Risk

An evidence-supported condition capable of materially impairing future
business performance, resilience, economic contribution, customer
durability, capability, continuity, or strategic execution if not
appropriately addressed.

Strategic Signal

An evidence-supported pattern or change sufficiently persistent,
material, structural, or consequential to indicate potential strategic
importance beyond normal operating variation.

Strategic Strength

An evidence-supported capability, operating condition, customer
relationship, management system, or economic characteristic materially
contributing to the sustained strength of the business and worthy of
deliberate protection.

Strategic Trade-Off

A material conflict between competing longer-term business benefits,
risks, capabilities, or objectives that cannot be fully optimized
simultaneously.

Strategic Unknown

A material strategic question for which available evidence is
insufficient to support a reliable conclusion or recommendation.

Strategy Execution Gap

The evidence-supported difference between Declared Strategic Intent and
the operating conditions, resource decisions, interventions,
capabilities, or behaviors required to make that intent real.

Temporal Evidence Lineage

The preservation of the evidence state available to MI at a particular
point in time, even when the originating source later corrects or
changes that data, so prior reasoning and decisions can be reconstructed
accurately.

Canonical Object Model Rules Added in v1.5

Metric Registry Rule: Metrics and KPIs are governed semantic
definitions over Evidence and Outcomes, not foundational canonical
reasoning objects.

Opportunity Consolidation Rule: Opportunity remains a
first-class business concept implemented as a governed Condition
type with lifecycle Evidence, Events, Relationships, Decisions, and
Outcomes.

Confidence Consolidation Rule: Evidence, Causal, Forecast,
Scenario, Pathway, and similar confidence concepts are dimensions,
not foundational objects.

Operational Wisdom Consolidation Rule: Operational Wisdom is a
mature Pattern state.

Economic Event Consolidation Rule: Economic Event is the
canonical Event object with economic classification and lineage.

Outcome State Integrity Rule: Actual, Desired, Expected,
Forecast, Scenario, Budget, and Target Outcomes remain semantically
distinct.

Human Authority Rule: MI may reason, recommend, model,
challenge, evaluate, and learn; authorized humans retain management
Decision authority.

Historical Integrity Rule: Prior intelligence and evidence
lineage are preserved when later evidence changes the conclusion.

Scale Neutrality Rule: One rooftop and enterprise use the same
canonical intelligence model.

Business-First Rule: MI starts with the business being managed
and scales outward.

Domain 11 Consolidation Note

Organizational & Multi-Store Intelligence is scale-activated rather than
scale-required. A one-rooftop tenant does not require artificial market,
region, or enterprise layers.

Domain 12 Consolidation Note

Domain 12 is Business & Strategic Intelligence, not enterprise-only
executive intelligence. It operates from a single owner/operator rooftop
through enterprise scale using the same canonical model.

Revision 1.5

Date: 2026-08-15
Change: Added Domain 11 and Domain 12 consolidation terminology;
froze the 11-family Canonical Object Model; added provenance, epistemic
status, historical/temporal lineage, Decision Authority, Scale
Neutrality, Business-First Intelligence, Responsible Management Role,
strategic/business terms, and cross-domain consolidation rules. Recorded
regression validation of Domains 2--12 and one-rooftop-to-enterprise
architecture during Session 025.

Canonical Reasoning Graph Terms --- Revision 1.6

Causal Strength

The governed strength of an MI causal conclusion. Canonical levels are
Association, Contributing Condition, Probable Primary Condition, and
Defensible Root Cause.

Competing Explanation Test

The requirement that MI evaluate material alternative explanations
supported by available business context before assigning strong causal
meaning.

Constraint Migration

A change in the location of the primary operating constraint after an
upstream Condition materially improves while the desired downstream
Outcome remains constrained.

Diagnostic Unknown

A detected Condition for which available Evidence is insufficient to
identify a sufficiently supported causal explanation.

Execution Effectiveness

The degree to which a selected Intervention was actually performed with
sufficient fidelity, completeness, and duration to test its intended
effect.

Execution Verification

The reasoning gate that establishes whether an Intervention was
meaningfully executed before MI attributes observed effects to it.
Canonical states include Verified Execution, Partial Execution,
Unverified Execution, and Non-Execution.

Condition Effectiveness

The degree to which an Intervention materially changed the specific
Condition it was intended to change.

Outcome Effectiveness

The degree to which the resulting Condition change produced the expected
downstream business Outcome.

Intelligence Effectiveness

The degree to which MI's diagnosis, recommendation, or management
pathway was useful in improving the quality of the management Decision
and subsequent business response.

Management Pathway

The smallest defensible, evidence-supported route by which management
can reasonably influence a material Condition or desired Outcome.

Pattern Candidate

A recurring evidence-supported relationship sufficiently notable to
warrant further validation but not yet mature enough for generalization.

Validated Pattern

A recurring relationship that persists with adequate Evidence and
sufficiently understood context to support governed reuse within its
validated boundaries.

Reasoning Error Classification

A classification applied to MI Effectiveness evidence describing why
prior reasoning was incomplete or incorrect, such as insufficient
Evidence, bad source, missing domain Evidence, faulty comparison, weak
causal rule, unseen Event, invalid Assumption, or context shift.

Canonical Reasoning Principles Added in v1.6

Management Decision Intelligence Principle

MI exists to improve the quality of management Decisions rather than
maximize information, alerts, problems, or recommendations.

Outcome ≠ Cause Principle

An unfavorable Outcome does not establish the Condition causing it. MI
reasons upstream before assigning causal meaning.

Integrity Principle

Diagnostic strength may not exceed the integrity and sufficiency of the
Evidence supporting it.

Competing Explanation Principle

Before assigning strong causal meaning, MI evaluates material
alternative explanations and reduces diagnostic confidence when
meaningful alternatives remain unresolved.

Diagnostic Restraint Principle

When Evidence cannot support a sufficiently reliable causal conclusion,
MI identifies uncertainty rather than manufacturing a diagnosis.

Management Relevance Principle

MI does not convert every detectable difference into management
intelligence. A Condition must be sufficiently material, consequential,
actionable, persistent, emerging, or decision-relevant to justify
management attention.

Controllability Principle

MI distinguishes what caused an Outcome from the portion of the causal
pathway management can reasonably influence.

Lowest Responsible Altitude Principle

MI directs intelligence to the lowest management role with sufficient
authority and capability to address the material Condition.

Root-Cause Compression Principle

When multiple downstream symptoms share a sufficiently supported
upstream Condition, MI prioritizes the smallest number of upstream
management pathways capable of materially improving the broader system.

Recommendation Proportionality Principle

The specificity and strength of an MI recommendation may not exceed the
strength of the Evidence, causal confidence, controllability, and
expected material benefit supporting it.

Management Challenge Principle

Management may challenge MI Intelligence by providing additional
Evidence, context, judgment, or alternative reasoning. MI evaluates that
contribution as governed Evidence rather than treating disagreement as
noncompliance.

Execution Before Effectiveness Principle

MI does not attribute an observed Outcome to an Intervention unless
Evidence sufficiently establishes that the Intervention occurred with
enough fidelity and duration to reasonably test its expected effect.

Constraint Migration Principle

When an upstream Condition materially improves but the desired Outcome
does not, MI re-evaluates the causal pathway to determine whether the
primary constraint migrated to another stage.

Decision Quality ≠ Outcome Quality Principle

MI evaluates Decision Quality using the Evidence, alternatives,
Assumptions, trade-offs, and uncertainty available when the Decision was
made rather than judging it solely by the eventual Outcome.

Transferability Principle

MI does not generalize a successful Intervention beyond its validated
context unless Evidence supports sufficient similarity in the material
Conditions governing its effectiveness.

Wisdom Decay Principle

Operational Wisdom remains subject to continuing Evidence and may be
weakened, narrowed, superseded, or retired when its predictive or
management value deteriorates.

Intelligence Unification Principle

When multiple MI domains identify Evidence related to the same
underlying management Condition, MI synthesizes that Evidence into the
smallest coherent set of Intelligence Objects rather than exposing
separate domain findings as independent management problems.

Complete Canonical Reasoning Loop

OBSERVE --- Business Reality → Evidence / Events / Outcomes
UNDERSTAND --- Integrity → Detection → Materiality → Condition
DIAGNOSE --- Competing Explanations → Causal Reasoning → Causal
Strength
FOCUS --- Controllability → Responsible Management Role →
Root-Cause Compression
ADVISE --- Management Pathway → Intelligence → Alternatives /
Recommendation
DECIDE --- Management Judgment → Decision / No-Action
ACT --- Intervention → Execution Verification
MEASURE --- Expected Effect → Condition Change → Outcome
EVALUATE --- Execution Effectiveness → Condition Effectiveness →
Outcome Effectiveness → MI Effectiveness
LEARN --- Observation → Pattern Candidate → Validated Pattern →
Operational Wisdom
ADAPT --- Updated reasoning → confidence → transferability →
improved future Intelligence → Observe again

Revision 1.6

Date: 2026-08-15
Change: Completed the Canonical Reasoning Graph in Session 026.
Added diagnostic gates, causal-strength semantics, recommendation and
management-challenge architecture, execution verification, separate
effectiveness dimensions, Constraint Migration, Decision Quality versus
Outcome Quality, Pattern maturity, transferability, Wisdom Decay, MI
self-correction, cross-domain arbitration, Intelligence Unification, and
the complete Observe → Understand → Diagnose → Focus → Advise → Decide →
Act → Measure → Evaluate → Learn → Adapt loop.