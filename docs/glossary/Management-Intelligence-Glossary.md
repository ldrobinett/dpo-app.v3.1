Management Intelligence™ Glossary

Version: 1.2  
Status: Active / Living Document  
Created: 2026-07-19  

Purpose

This glossary establishes the canonical language of Management Intelligence™. Terms defined here should be used consistently across specifications, ADRs, APIs, user interfaces, tests, and operating documentation.

Where a term has a broader industry meaning, this document defines its meaning within the platform.

A

Acceptance Test

A test that verifies a specified business behavior using defined inputs, conditions, and expected outcomes.

Action

A management or operational step taken in response to an observation, risk, opportunity, or recommendation.

Actual Production

The completed production credited during a defined period, measured using the approved source and accounting rules.

Advisor

A service employee responsible for client communication, repair-order development, presentation of findings, and coordination of authorized work.

B

Baseline

A defined reference point used to compare current performance, such as prior year, prior period, budget, target, or peer group.

Business Object

A canonical representation of an entity or concept used across the platform, such as Store, Technician, Repair Order, Observation, or Recommendation.

Business Rule

An approved, testable statement that controls how data is interpreted, calculated, classified, or acted upon.

C

Capacity

The amount of work an operation can reasonably produce during a period based on available people, skills, time, facilities, equipment, and constraints.

Confidence

A stated level of certainty attached to an intelligence output based on evidence quality, completeness, consistency, and model or rule reliability.

Constraint

A condition that limits execution, production, conversion, timing, or expected impact.

Controllable Opportunity

An identified opportunity that can be influenced through available management or operational action.

Core Measurement

A directly observed or explicitly calculated value owned by a domain.

Customer Intelligence

The domain responsible for understanding client behavior, experience, retention, communication, demand, and related customer outcomes.

D

Daily Operating Standard

A defined behavior or management process expected to occur consistently during the operating day.

Daily Production Objective (DPO)

The production expectation for a defined period, person, team, department, or store, based on approved productivity, availability, and operating assumptions.

Data Freshness

The age of data relative to the time it is expected to be available and useful.

Data Grain

The level at which data is represented, such as transaction, repair order, technician-day, store-day, month, or market.

Derived Intelligence

A domain-owned conclusion created by combining measurements, context, trends, thresholds, business rules, and constraints.

Domain

A bounded area of business knowledge with explicit ownership, rules, inputs, outputs, and responsibility.

Domain Boundary

The formal line defining what a domain owns, consumes, produces, and intentionally does not own.

Domain Intelligence

Measurements, observations, risks, opportunities, forecasts, and explanations produced by a domain from its owned business knowledge.

E

Evidence

The source data, measurements, rules, trends, and context that support an intelligence conclusion or recommendation.

Execution Intelligence

The domain responsible for evaluating whether approved operating processes and behaviors are occurring with the expected completion, timing, quality, and consistency.

Explainability

The ability to trace a material conclusion or recommendation to its source data, rules, calculations, assumptions, time period, confidence, and limitations.

Expected Impact

The estimated financial, operational, customer, or organizational result of addressing a risk or acting on an opportunity.

F

Financial Intelligence

The domain responsible for understanding revenue, gross profit, expense, budget, trend, mix, margin, absorption, and financial consequence.

Forecast

An estimate of a future condition or result based on current evidence, assumptions, trends, and known constraints.

Forecast Production

The amount of production expected by the end of a defined period based on current pace, remaining time, available capacity, and known constraints.

H

Health Indicator

A domain output that describes whether an operation, process, workforce, or result is within an acceptable or sustainable range.

Hours Remaining

The amount of productive labor still required or available within a defined period, depending on the specified context.

I

Intelligence

Contextual, explainable understanding that improves a decision. Intelligence goes beyond reporting by identifying meaning, risk, opportunity, likely outcome, or required attention.

Intelligence API

A versioned interface that exposes domain intelligence, recommendations, explanations, and related platform objects to approved consumers.

Intelligence Domain

See Domain.

Intelligence Output

A domain-produced observation, health indicator, risk, opportunity, forecast, constraint, or explanation.

K

Key Performance Indicator (KPI)

A measurement selected because it represents progress toward a material business objective. Not every metric is a KPI, despite humanity's heroic efforts to label everything important.

L

Learning Engine

The platform component responsible for evaluating outcomes, comparing predicted and actual impact, identifying patterns, and proposing governed improvements without silently rewriting approved rules.

M

Management Intelligence™

A governed platform that observes business operations, reasons through specialized domains, identifies risk and opportunity, explains conclusions, recommends prioritized actions, and learns from outcomes while preserving human decision authority.

Measurement

A quantified value derived from observed data according to a defined rule, unit, grain, and time period.

Metric

A repeatable quantitative measure. A metric becomes a KPI only when it is tied to a material objective.

Milestone

A defined project capability or outcome with objective deliverables and exit criteria.

O

Observation

A factual, time-aware statement produced from validated data without yet prescribing an action.

Opportunity

A supported condition in which feasible action can produce meaningful improvement.

Opportunity Indicator

A domain-owned signal that identifies realistic, actionable upside and includes supporting evidence, constraints, and estimated impact.

Organizational Intelligence

The domain responsible for understanding workforce structure, skill, capacity, sustainability, leadership coverage, dependency, and organizational risk.

Outcome

The measured result that follows an action or recommendation.

P

Pace

The rate at which a result is being produced relative to elapsed time and a defined target or comparison.

Production Intelligence

The domain responsible for understanding production objectives, actual production, pace, recovery, capacity, technician availability, forecast production, WIP coverage, and hours remaining.

Production Pace

The relationship between actual production and expected production at a defined point in time.

ProdTracker

The product application evolving into the Management Intelligence™ platform. ProdTracker may remain the product name while Management Intelligence™ describes the platform architecture and capability.

R

Recommendation

A prioritized, explainable action synthesized by the Recommendation Engine from domain evidence, risk, opportunity, constraints, expected impact, urgency, and confidence.

Recommendation Engine

The only platform component authorized to synthesize and issue final recommendations across one or more intelligence domains.

Recovery

The additional production or execution required, beyond current pace, to reach a defined objective within the remaining period.

Release

A versioned, validated product state approved for a defined environment or user group.

Risk

A supported condition that threatens performance, sustainability, financial results, customer outcomes, or operational reliability.

Risk Indicator

A domain-owned signal that identifies a material threat and includes trigger logic, severity, evidence, and clear conditions.

S

Session

A numbered work record documenting objectives, decisions, artifacts, commits, open questions, and next steps. A session records effort; it does not itself prove completion.

Signal

A meaningful change, pattern, threshold crossing, or condition derived from one or more measurements.

Source of Truth

The authoritative system, object, or domain responsible for the official representation of a value or concept.

Store

A dealership operating entity represented within the platform and bounded by tenant, market, brand, and organizational context.

Sustainability

The ability to maintain required performance over time without unacceptable dependency, overload, skill imbalance, or organizational fragility.

T

Target

An approved expected level of performance used to guide operations and evaluate results.

Technician Availability

The productive time a technician can reasonably contribute during a defined period after considering schedule, absence, training, assignment, and known constraints.

Technician Sustainability Index (TSI)

A measure of workforce progression, skill development, knowledge transfer, mentoring leverage, and pay alignment that indicates whether technician capability can be sustained and expanded over time.

TSI is not simply retention. It evaluates whether the organization is developing future capability rather than depending indefinitely on existing expertise.

Tenant

The highest enforced data-isolation boundary for a customer or organization using the platform.

Threshold

A governed value used to classify or trigger a condition. Thresholds require context and should not be treated as universal truth without review.

Trend

The direction and rate of change observed across a defined sequence of periods.

U

User Interface (UI)

The presentation and interaction layer through which users consume intelligence and record actions. The UI is not the authoritative owner of business logic.

Utilization Variance Index (UVI)

A measure of production concentration and dependency across technicians. UVI indicates how heavily an operation depends on a small number of individuals and the risk created when those individuals are absent, unavailable, retire, or leave.

A high UVI suggests fragile production concentration. A lower, balanced UVI generally indicates production is distributed more sustainably, subject to skill mix and business context.

V

Version

A controlled identifier for a document, rule set, contract, model, or product state.

W

Work in Process (WIP)

Authorized or active work that has not yet been fully completed, posted, closed, or otherwise resolved according to the applicable operating definition.

WIP Coverage

The relationship between available work and the production capacity or objective it is expected to support.

Worked Example

A realistic scenario demonstrating how defined inputs, rules, calculations, and outputs behave.

Terminology Rules

Use measurement for a quantified value.

Use observation for a factual interpretation of validated data.

Use signal for a meaningful change or condition.

Use risk or opportunity only when evidence and domain rules support the classification.

Use recommendation only for an output of the Recommendation Engine.

Use target, budget, forecast, and actual distinctly.

Do not use intelligence as a decorative substitute for reporting.

Define acronyms on first use in user-facing and architecture documents.

Additional Canonical Architecture Terms

Actionable Need

A legitimate vehicle or customer need supported by sufficient evidence to warrant an appropriate recommendation, estimate, presentation, follow-up, or operational action.

Authorization

A customer decision approving a presented recommendation or estimate. Authorization is distinct from completion.

Benchmark

A comparative reference used to provide context for performance. A benchmark does not become a tenant target or desired outcome unless the tenant explicitly adopts it.

Canonical

A standardized system-level concept used by Management Intelligence™ regardless of terminology used by a specific tenant, OEM, vendor, source system, or dealership.

Capability Envelope

The range and complexity of work a person, team, or operation can reasonably perform based on demonstrated skill, training, certification, experience, equipment, and operating conditions.

Conversion Rate

The percentage of legitimate presented opportunities that result in customer authorization.

Formula: Authorized Opportunities ÷ Legitimate Presented Opportunities.

A general 25%–50% range may be useful as guided setup context, but tenant interpretation remains configurable.

Deferred Opportunity

A legitimate actionable need identified but not completed that remains potentially applicable to a future service event.

Desired Outcome

A business result the tenant has identified as important for management. It may be based on budget, forecast, year-over-year improvement, OEM objectives, internal objectives, benchmarks, trends, or other tenant-selected priorities.

Discovery Gap

An evidence-supported difference between actionable needs actually identified and the legitimate actionable need MI estimates was reasonably present within the evaluated population.

Evaluation

The process of appropriately checking, measuring, testing, diagnosing, reviewing, or validating whether a legitimate need exists.

Evaluation Gap

The eligible population that reasonably should have been evaluated but was not.

Guided Configuration

A tenant setup process in which MI provides recommended starting values, operating context, expected consequences, and evidence-based guidance while preserving tenant authority.

Materiality

The degree to which the magnitude and consequence of a condition justify management attention relative to other available risks, opportunities, constraints, and actions.

Missed Opportunity Capture Assumption

A tenant-configurable percentage applied to estimated legitimate opportunity lost through an identified execution gap to estimate the portion reasonably recoverable through management action. MI may guide setup around 30%. Scenario assumptions may be tenant configured, including 25% Conservative, 50% Aggressive, and 75% Aspirational.

Non-Evaluated

An eligible service event, vehicle, item, or opportunity basis that reasonably should have received an applicable evaluation but did not.

Ontology

The governed model of canonical concepts and the relationships among them. A taxonomy organizes classifications; an ontology additionally describes how concepts relate, interact, depend on one another, and influence outcomes.

Opportunity Basis

The evidence or operating condition from which a legitimate service opportunity can originate, including customer request, due maintenance, deferred work, inspection, diagnosis, vehicle condition, OEM requirement, or tenant-configured policy.

Opportunity Conversion Intelligence (OCI)

A proprietary MI reasoning capability that analyzes how effectively legitimate presented opportunities become authorized work and identifies material patterns that may explain conversion performance. OCI is intelligence, not merely a visible score.

Opportunity Discovery Intelligence (ODI)

A proprietary MI reasoning capability that assesses whether legitimate actionable opportunities are being discovered at a rate reasonably supported by the evaluated vehicle population and available evidence. ODI is intelligence, not merely a visible score.

Opportunity Gap

A supported point of leakage within the service-opportunity lifecycle that may represent recoverable operational or financial opportunity.

Opportunity Lineage

The traceable relationship of an opportunity across its lifecycle, evidence, estimates, presentations, decisions, authorizations, completion, deferral, recovery, and financial consequence.

Opportunity Lifecycle

The canonical progression used by MI to reason about legitimate service opportunity:

Opportunity Basis → Eligibility → Evaluation/Validation → Actionable Need Identified → Estimate/Recommendation Created → Presented → Customer Decision → Authorization → Completion → QA/Delivery → Outcome.

Opportunity Recovery

The process of appropriately revisiting a legitimate deferred opportunity while it remains valid and relevant.

Promise at Risk

A service event whose current evidence indicates a material likelihood that an established customer promise, completion expectation, or communication commitment will not be met without intervention.

Relevant & Valuable Display

A role-appropriate presentation of intelligence that materially helps the intended user understand a condition, evaluate evidence, make a decision, or execute an action. MI performs the analysis; displays communicate the necessary intelligence.

Taxonomy

A structured classification and hierarchy used to organize related canonical concepts into defined categories.

Tenant Configuration

The governed objectives, terminology, assumptions, standards, rules, priorities, and operating practices selected by a tenant and mapped onto the canonical MI model.

Tenant Intelligence

An organization-specific intelligence layer that maps a tenant's terminology, objectives, standards, processes, data, and management practices onto the canonical Management Intelligence™ architecture without altering the canonical foundation.

Tenant Mapping

The governed translation between tenant, OEM, vendor, or source-system terminology/data structures and canonical MI concepts.

Technician Discovery Profile

An internal MI intelligence object describing the type, frequency, and condition distribution of legitimate service opportunities identified by a technician, normalized where evidence permits for evaluated population, vehicle/work mix, capability, and relevant context.

Technician Dependency Profile

An internal MI assessment of the degree to which an operation depends on an individual technician or small group for production, capability, and legitimate opportunity discovery.

Upstream Principle

MI should look first for the earliest material controllable condition capable of explaining or changing a downstream result.

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

Evaluation Principle: MI measures what reasonably should have been evaluated and was not.

Discovery-at-Origin Principle: Discovery is analyzed where legitimate opportunity is created, not only where the sale is recorded.

Opportunity Lineage Principle: MI preserves opportunity lineage so overlapping gaps are not counted multiple times.

Tenant Intelligence Principle: MI provides canonical reasoning; Tenant Intelligence maps an organization's terminology, objectives, standards, processes, data, and practices onto it.

Guided Configuration Principle: MI provides informed setup guidance while preserving tenant authority.

Relevant & Valuable Display Principle: MI performs analysis; displays communicate only what the intended role needs to understand, decide, or act.

Management Attention Principle: MI prioritizes the smallest number of evidence-supported actions with the greatest reasonable ability to improve the tenant's desired outcome.

No Forced Action Principle: MI may conclude that no material controllable constraint exists and recommend no intervention.

Revision History

Version

Date

Change

1.0

2026-07-19

Initial glossary created during Session 009

1.1

2026-08-15

Added Domain 7 opportunity architecture, tenant-neutral terminology, guided configuration, ODI/OCI, technician discovery/dependency, acronym library, and display/action principles during Session 019

Revision 1.2

Date: 2026-08-15
Change: Added Domain 8 workforce, capability, coverage, leadership, succession, intervention effectiveness, MI self-evaluation, MI Effectiveness Score, quarterly review, and people-evidence architecture during Session 020.