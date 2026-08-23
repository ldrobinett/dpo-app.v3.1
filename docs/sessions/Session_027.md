Session 027 --- MI V5 Build Architecture: Layer 1

Evidence Acquisition & Source Integration

Date: August 23, 2026
Status: FROZEN / VETTED / COMPLETE

Session Purpose

Define Build Architecture Layer 1: how business reality enters
ProdTracker while preserving source meaning, provenance, timing,
auditability, continuity, security, and compatibility from a single
non-integrated rooftop through a multi-DMS enterprise.

Foundational Boundary

The Evidence Acquisition & Source Integration Layer acquires and
preserves reality. It does not interpret reality.

Layer 1 may determine what Evidence exists, where it came from, what
canonical business concept it maps to, whether it is
complete/current/valid, and which governed Evidence state downstream
systems should use. It does not diagnose performance, determine root
cause, recommend action, judge effectiveness, or decide what management
should see.

1. Integration Independence

MI V5 supports three simultaneous acquisition modes: 1. Native
Integration --- CDK, Reynolds, Tekion, Dealertrack, future approved
sources. 2. Managed Import --- SDL, CSV, Excel,
DMS/OEM/accounting/MPI exports and governed files. 3. Human-Declared
Evidence --- manager morning MTD entry, ASM route sheet, technician
flagging, management context, approved declarations.

All feed the same canonical MI architecture.

Integration Independence Principle

Management Intelligence capability must not depend on native DMS
integration when equivalent governed Evidence can be acquired through
approved import or human-declared methods. Native integration improves
automation, timeliness, granularity, verification, and confidence
rather than creating a separate intelligence architecture.

V4's non-integrated workflow remains a legitimate operating mode,
onboarding path, audit mechanism, and continuity fallback.

2. Evidence Authority & Reconciliation

Evidence precedence considers source authority for the specific Evidence
Type, semantic purpose, granularity, freshness, verification status, and
reconciliation policy.

Possible states: Single Source, Corroborated, Reconciled, Conflicting,
Superseded, Corrected.

Evidence Authority Principle

The governing Evidence source is determined by Evidence Type, semantic
purpose, source authority, freshness, verification, and applicable
reconciliation policy rather than by a universal source hierarchy or
latest-value rule.

Evidence Conflict Principle

Material unresolved Evidence conflicts remain preserved, reduce
dependent confidence, and do not produce a false authoritative value.

Graceful Degradation Principle

Loss of a preferred Evidence source may reduce automation, timeliness,
granularity, or confidence, but should not unnecessarily disable MI
when approved alternate Evidence paths remain available.

3. Cadence, Latency & Business Time

Latency classes: - L0 Event: seconds/minutes. - L1 Intraday:
approximately 5--60 minutes. - L2 Daily: daily/overnight. - L3
Periodic: weekly/monthly. - L4 Contextual: on change/as available.

Cadence Separation Principle

Evidence acquisition frequency, MI reasoning frequency, and management
communication frequency are separate architectural decisions.

Material Re-evaluation Principle

Late, corrected, or superseding Evidence reopens Intelligence only
when materially relevant to its Conditions, Outcomes, Assumptions,
Decisions, or reasoning lineage.

Absence-of-Evidence Principle

Missing expected Evidence is not interpreted as zero business
activity.

Business-Time Principle

MI reasons using applicable effective business time, timezone,
operating-day definition, and reporting period rather than ingestion
time alone.

Continuous Intelligence Principle

MI processes Evidence at the cadence appropriate to its source and
management purpose while communicating only sufficiently material
changes warranting management awareness or Decision.

4. Failure, Recovery & Resilience

Canonical failure states: Source Unavailable, Connection Failure,
Invalid Evidence, Partial Ingestion, Processing Failure,
Recovery/Replay.

Durable Acquisition Principle

Once source Evidence is successfully acquired, MI preserves sufficient
payload and provenance for safe reprocessing without unnecessary
reacquisition.

Completeness Before Interpretation Principle

An acquired dataset is not treated as representative of its intended
business population until applicable completeness checks pass or
incompleteness is explicitly represented downstream.

Invalid records may be quarantined without unnecessarily blocking valid
records.

Failure Relevance Principle

Technical failures interrupt management only when they materially
affect availability, confidence, timeliness, or decision relevance of
Management Intelligence.

Recovery Integrity Principle

Recovery restores Evidence from the last known completeness boundary
using replay, deduplication, reconciliation, and applicable fallback
sources without duplicating business effects or destroying historical
lineage.

Source health: HEALTHY, DELAYED, DEGRADED, FAILED, RECOVERING.

5. Operational Continuity Instructions

Each material source may define a Fallback Operating Procedure
identifying primary/alternate sources, responsible role, temporary
action, affected Intelligence, recovery behavior, and notification
requirements.

Operational Continuity Principle

When source degradation requires temporary human action, MI informs
the appropriate Responsible Role what changed, what Intelligence is
affected, what temporary action is required, and when normal procedure
may resume.

Recovery Closure Principle

When the preferred source is restored, MI reconciles alternate
Evidence, identifies unresolved material conflicts, and explicitly
releases affected users from temporary fallback procedures.

6. Source Mapping, Schema & Versioning

Mapping may occur at vendor, tenant, store, and business-taxonomy
levels. Mappings and schemas are versioned and effective-dated.

Source Abstraction Principle

Source-specific structures, terminology, identifiers, and technical
behavior are translated at acquisition so downstream MI operates on
stable canonical semantics.

Mapping Governance Principle

MI may recommend mappings, but material semantic mappings become
authoritative only through governed validation or approved
deterministic evidence.

Configuration-Not-Fork Principle

Tenant variation is represented through governed configuration rather
than tenant-specific forks of the canonical MI model.

Mapping Historical Integrity Principle

Mapping changes preserve the interpretation applicable to historical
Evidence and trigger targeted reprocessing when corrections materially
alter business meaning.

Identity Integrity Principle

MI does not merge source identities into a canonical Entity without
sufficient evidence they represent the same real-world Entity.

7. Security, Entitlement & Tenant Isolation

Three gates remain distinct: 1. Entitlement --- did the customer
purchase it? 2. Permission --- may this user access it? 3.
Relevance --- should MI surface it now?

Tenant Isolation Principle

Evidence, derived state, Intelligence, configuration, and learning
remain isolated within the authorized tenant boundary unless an
explicitly governed cross-tenant capability permits otherwise.

Permission Propagation Principle

Derived Evidence and Intelligence inherit applicable restrictions from
materially contributing source Evidence unless a governed
transformation permits broader disclosure without exposing restricted
information.

8. DMS Operational Continuity Mode

ProdTracker may provide DMS Continuity Mode during a material DMS
outage to sustain minimum necessary Service and Parts operations,
preserve continuity Evidence, maintain customer
authorization/transaction lineage, provide management visibility, and
reconcile activity after recovery.

DMS Operational Continuity Capability

When a material DMS outage prevents normal dealership operation,
ProdTracker may provide governed Continuity Mode enabling authorized
users to capture the minimum customer, vehicle, repair-order, labor,
parts, authorization, payment-status, and operational Evidence
required to continue service operations, followed by governed
reconciliation to authoritative records.

Continuity Minimum Necessary Principle

Continuity Mode captures only what is necessary for safe, practical
operation and post-recovery reconciliation. It does not become a full
replacement DMS.

System-of-Record Boundary Principle

Continuity Evidence does not silently assume authoritative DMS,
accounting, tax, warranty, inventory, or payment-processing
responsibility.

Trusted Recovery Principle

Following a security-related or integrity-uncertain interruption,
authoritative source status is not restored until applicable trust,
validation, and administrative recovery requirements are satisfied.

9. Continuity RO

The customer-facing Service workflow uses a Continuity RO,
canonically supported by existing objects rather than adding a new
canonical object.

It supports customer/vehicle/VIN/mileage, advisor/visit/promise,
multiple repair lines, concerns, technician assignment, multiple labor
and parts entries, estimates/revisions, approval/decline, payer
allocation,
labor/parts/supplies/fees/taxes/deductibles/credits/adjustments, payment
status/method/reference without raw card credentials,
completion/delivery, and audit history.

Financial Aggregation Integrity Principle

Continuity RO financial values originate from transaction detail and
aggregate through governed line-level and RO-level calculations.
Labor, parts, supplies, fees, taxes, deductibles, payer
responsibility, payments, credits, and adjustments remain separately
identifiable.

10. Estimates, Legal Language & Authorization

Signed estimates preserve the exact state presented. Changes create
revisions rather than overwrite prior authorization history.

Legal Template Integrity Principle

ProdTracker does not dynamically generate or materially alter
customer-facing legal authorization language. Applicable terms are
supplied/approved through governed tenant templates, versioned by
jurisdiction/effective period, and preserved with the applicable
transaction and authorization.

Customer Authorization Integrity Principle

Every customer authorization is bound to the specific Continuity RO,
repair lines, estimate version, monetary amount, legal-template
version, authorization method, identity evidence, and timestamp.
Subsequent changes create new revisions.

Rendered/signed document snapshots are preserved.

11. Parts Continuity

Parts records line-specific requested, issued, returned, and net-used
quantities, plus applicable cost/sale values and timestamps.

Parts Continuity Principle

Parts may record line-specific requests, issuance, returns,
quantities, cost and sale values subject to permission, producing line
and RO totals while preserving sufficient detail for post-recovery
inventory and financial reconciliation.

12. Parts Movement Ledger & Non-RO Activity

Continuity supports discrete parts IN/OUT movement for RO and non-RO
activity: receipts, RO issues/returns, retail/wholesale sales and
returns, transfers, cores, approved adjustments, and governed other
types.

A Continuity Parts Invoice supports wholesale and retail activity
outside an RO.

Parts Movement Integrity Principle

Continuity parts movement is recorded as discrete, auditable IN/OUT
Events identifying part, quantity, movement type, associated RO/line
or non-RO transaction, responsible user, effective time, and
applicable cost/sale Evidence.

Physical/Financial Separation Principle

Physical inventory movement remains separate from financial
billing/posting so MI can distinguish what physically occurred from
what has been financially recognized.

Continuity Inventory Principle

ProdTracker may calculate expected inventory from the last
authoritative state plus recorded continuity movements. It remains
Continuity Evidence until reconciled with the authoritative inventory
system.

13. Pre-Outage WIP Continuity

Continuity covers the entire open workload: 1. Pre-Outage WIP, Still
Open. 2. Pre-Outage WIP, Completed During Outage. 3. New RO Created
During Outage.

WIP Continuity Principle

At Continuity activation, ProdTracker preserves the last known
authoritative state of existing open ROs and permits subsequent
Events, lines, labor, parts, estimates, authorizations, payments, and
completion activity against those existing RO identities. Original DMS
identity, opening date, aging, and historical state remain intact.

Continuity Completion Principle

Pre-outage WIP completed, paid, or delivered during an interruption is
reconciled back to the original authoritative DMS RO rather than
represented as a duplicate replacement RO.

14. Recovery & Reconciliation

Recovery includes trust/health restoration, replay from
checkpoint/watermark, idempotent processing, source reconciliation,
matching outage-created ROs to official DMS ROs, reconciling pre-outage
WIP to original ROs, Service financial reconciliation, Parts/inventory
reconciliation, payment reconciliation, exception worklists,
responsible-role review, and governed completion.

Reconciliation Completion Principle

A Continuity Transaction remains unresolved until required
authoritative DMS, financial, parts, payment, and other applicable
records have been matched or entered, material discrepancies resolved
or explicitly accepted, and governed reconciliation completion
reached.

15. Layer 1 Formal Contract

Responsibilities

Source connectivity/acquisition; source and ingestion contracts; schema
validation; mapping/versioning; identity-resolution mechanics;
deduplication/idempotent ingestion; evidence reconciliation mechanics;
source reliability; provenance; completeness/freshness;
checkpoints/watermarks/replay; quarantine/recovery; failover; tenant
isolation; sensitivity propagation; source health; continuity
acquisition/recovery mechanics.

Inputs

Native integrations; managed imports; human-declared Evidence;
source/tenant/store configuration; authority/reconciliation policy;
mapping/taxonomy configuration; cadence/freshness policy;
security/entitlement configuration.

Outputs

Canonically mapped Evidence; canonical Entity references; provenance;
acquisition/effective timestamps; authority/reconciliation state;
completeness/freshness state; confidence inputs; source health;
mapping/schema versions; exception/quarantine records; downstream
change/event triggers.

Dependencies

Tenant Registry; authentication/authorization infrastructure; canonical
definitions/contracts from Layer 2; governed configuration/version
management; downstream evidence requirements.

Must Never Own

Layer 1 does not determine performance judgment, business materiality,
root cause, management responsibility, recommendations, management
pathways, intervention effectiveness, Operational Wisdom, or final
Relevant & Valuable Display.

Its boundary ends at: > What Evidence do we have, where did it come
from, what does it canonically correspond to, how
trustworthy/current/complete is it, and what governed Evidence state
should downstream systems use?

16. Final Smoke Test

Passed: single-store V4/manual workflow; full integration; mixed-DMS
enterprise; source outage/failover; malformed/partial datasets; mapping
corrections; schema changes; tenant isolation; restricted People
Intelligence; long DMS outage; Service continuity; Parts continuity;
wholesale/retail continuity; pre-outage WIP completion; post-recovery
reconciliation.

FINAL STATUS: FROZEN / VETTED / COMPLETE

17. Future Product Architecture Pin --- Customer Engagement Intelligence

Preserve outside current scope a future myKaarma-type customer
engagement platform made materially stronger by MI V5 / Digital FOD
intelligence.

Potential surface: messaging, video, estimate presentation, approvals,
payments, repair-status communication, follow-up, and customer
interaction history.

Customer engagement is the execution surface. MI is the management
brain behind it.

MI could identify missed presentation/follow-up, determine actions,
escalate when appropriate, measure outcomes, and learn which
interventions work.

18. Session Vocabulary

Term                Pronunciation                  Plain-English           MI V5 Example
Definition

Canonical           kuh-NON-ih-kul                 The agreed              Different DMS
authoritative           advisor fields
representation inside a map to one
system.                 Service Advisor
concept.

Taxonomy            tak-SON-uh-mee                 An organized            Tires, Brakes,
classification system.  Batteries,
Alignments under
Controllables.

Idempotency         eye-dem-POH-tən-see            Repeating the same      Replaying a
operation does not      closed-RO event
duplicate its business  still counts it
effect.                 once.

Checkpoint          CHECK-point                    A saved recovery        Resume after the
position.               last confirmed
event.

Watermark           WAW-ter-mark                   The latest point        All RO events
through which data is   through 10:17 AM
known                   processed.
complete/processed.

Quarantine          KWOR-an-teen                   Isolating invalid data  Malformed records
from valid processing.  held for review.

Failover            FAIL-oh-ver                    Switching to an         CDK feed fails
approved backup         and SDL/manual
source/system.          process
temporarily
governs.

Queue               cue                            A holding line for work Evidence waits
waiting to be           safely during a
processed.              processing
interruption.

Backoff             BACK-off                       Increasing delay        API retries
between repeated        become less
retries.                frequent during
persistent
failure.

Dead-Letter Queue   DEAD LET-er cue                Holding area for        One bad RO does
records that repeatedly not block the
fail processing.        feed.

Schema              SKEE-muh                       Defined structure of    RO number, VIN,
data and its            advisor ID, labor
fields/relationships.   sale, timestamps.

Mapping             MAP-ing                        Defining how one        4WA maps to
system's value          ALIGNMENT.
corresponds to another.

Versioning          VER-zhun-ing                   Tracking changes over   Mapping v1.1
time.                   replaces v1.0
without erasing
history.

Identity Resolution eye-DEN-tih-tee                Determining different   DMS Tech 4821 and
rez-uh-LOO-shun                identifiers represent   payroll 009734
the same real entity.   are one
technician.

Contract            KON-trakt                      Explicit agreement      Every adapter
defining what a         delivers through
component provides.     the Canonical
Ingestion
Contract.

Validation          val-ih-DAY-shun                Checking conformance to A nonnumeric
required                gross value fails
rules/structure.        validation.

Schema Evolution    SKEE-muh ev-uh-LOO-shun        Changing data structure Adding technician
while preserving        skill
historical/compatible   classification
use.                    without
invalidating old
Evidence.

Backward            BACK-werd                      Newer versions still    New ingestion
Compatibility       kum-pat-uh-BIL-ih-tee          work correctly with     schema still
older                   handles
information/behavior.   historical
Evidence.

Authentication      aw-then-tih-KAY-shun           Proving who a           Confirming
user/system is.         connected
DMS/user
identity.

Authorization       aw-thur-ih-ZAY-shun            Determining what an     Parts can edit
authenticated           parts entries but
user/system may do.     not restricted
People
Intelligence.

De-identification   dee-eye-den-tih-fih-KAY-shun   Reducing/removing       Preparing future
identifying linkage.    cross-tenant
benchmarks.

Referential         ref-er-EN-shul in-TEG-rih-tee  Keeping related records Continuity RO
Integrity                                          linked to the correct   links to the
record.                 correct final DMS
RO.

Immutable           ih-MYOO-tuh-bul                Not silently changeable Signed Estimate
after recording.        v1 remains
preserved when v2
is created.

Non-repudiation     non ree-pyoo-dee-AY-shun       Strong evidence         Preserve what was
supporting that an      authorized, by
action/authorization    whom, how, and
occurred.               when.

Aggregation         ag-rih-GAY-shun                Combining detailed      Parts entries →
values into meaningful  line total → RO
totals.                 total.

Ledger              LEJ-er                         Organized record of     Parts Movement
transactions and        Ledger.
changes.

Perpetual Inventory per-PETCH-oo-ul IN-ven-tor-ee  Continuously updated    Continuity
expected quantity on    Expected On-Hand
hand.                   from DMS baseline
plus movements.

Resume Point

Build Architecture --- Layer 2: Canonical Business Model

Starting question: > What stable business objects and relationships
must MI understand so every source, domain, reasoning process,
continuity capability, and management experience speaks the same
business language?