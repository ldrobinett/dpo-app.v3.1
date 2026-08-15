MI v5 --- Session 0017

Domain 5: Parts Operations --- Inventory, Fulfillment, Financial Performance & Management Attention

Date: August 14, 2026
Project: ProdTracker Management Decision Platform --- Management
Intelligence v5
Status: Architecture / Domain Definition
Session Outcome: Domain 5 --- Parts Operations v1 FROZEN

1. Session Purpose

Define the canonical architecture for Domain 5 --- Parts Operations
while preserving a central product requirement:

The depth belongs inside MI, not in the manager's workload.

Parts must be understood in two roles:

Financial engine

Upstream operational enabler or constraint on Service production

The session established Parts Inventory Health, availability,
fulfillment, SOR/backorder management, financial/channel performance,
and a new foundational MI doctrine: the Management Attention
Principle.

2. Management Attention Principle --- FROZEN

MI should absorb operational complexity, identify the earliest
material controllable constraint, and present management with the
minimum number of prioritized actions necessary to improve
performance. Supporting complexity remains available as evidence, not
as required management workload.

Three-Level Experience

Management Attention --- What requires action now?

Evidence --- Why does MI believe the issue deserves attention?

Underlying Data --- What transactions, ROs, parts, technicians,
trends, and calculations produced the conclusion?

The manager begins at Level 1.

MI should consider degree of deviation, financial impact, operational
impact, persistence, controllability, and relationships among
constraints before elevating an issue.

Complexity belongs in the system. Management receives the fewest
actionable items necessary to materially improve the operation.

3. Domain 5 Core Architecture

Parts Operations v1 contains four major components:

Inventory Health

Fulfillment & Service Support

SOR & Backorder Management

Financial & Channel Performance

The MI intelligence layer operates across all four.

PART I --- INVENTORY HEALTH

4. Inventory Health Framework --- FROZEN v1

Inventory Health is evaluated as a system:

Quantity → Velocity → Quality → Availability

No single measure such as DSO, Turns, or Fill Rate is sufficient to
determine inventory health.

Quantity

Management question: Is the inventory investment appropriate for the
demand the operation needs to support?

Canonical measures: - Inventory $ - DSO / Days Supply on Hand -
Tenant/OEM target or expected inventory range

DSO estimates how many days the current inventory can support expected
demand at the current usage/sales rate. Lower DSO is not automatically
better. Too much inventory creates working-capital and obsolescence
exposure; too little can damage Service availability and production.

Velocity

Management question: Is the inventory moving at an appropriate rate?

Canonical measures: - Inventory Turns - Consumption / movement trend

DSO and Turns may describe the same underlying condition and should not
automatically create separate management alerts.

Quality

Management question: How much inventory investment is productive
versus trapped or approaching obsolete capital?

Default canonical dealership aging buckets:

Age             Classification           MI Interpretation

0--4 months     Current                  Normal active inventory
4--6 months     Aging                    Early aging / monitor
7--9 months     Aged                     Increasing inventory risk
10--12 months   Technical Obsolescence   Immediate management concern
12+ months      Obsolescence             Obsolete inventory

Tenants may override these thresholds.

The Freight Train

The 10--12 month bucket is formally Technical Obsolescence. The
management term Freight Train is retained because management can see
the collision coming before inventory crosses into 12+ month
obsolescence.

Future MI should evaluate migration: - 7--9 → 10--12 - 10--12 → 12+

MI should eventually distinguish Legacy Obsolescence from New
Obsolescence Generation.

Availability

Management question: Does Parts have what customers and technicians
actually need when demand occurs?

Core measures where source data supports them: - Fill Rate -
Stock-outs - Buyouts / Emergency Purchases - Backorders - Special
Orders - Lost Sales

Optional/source-dependent: First-Time Fill Rate.

First-Time Fill Rate should not create manual workload merely to produce
a KPI.

5. Stock-out vs Buyout

Stock-out: Demand occurs for a part not available from the store's
own inventory when needed.

Buyout / Emergency Purchase: The store purchases the required part
outside its normal inventory/OEM supply channel to satisfy demand.

Backorder: A required part is ordered through the normal supply
channel but the supplier/OEM cannot currently fulfill it.

Special Order: A non-stocked part is intentionally ordered for a
specific customer or RO.

An availability event is evidence, not automatically a management
failure.

MI evaluates frequency, recurring demand, economics, stocking policy,
cost, expected demand, and supply conditions before identifying a
stocking constraint.

6. Inventory Mix Intelligence

A key condition:

Inventory $ / DSO     High
Turns                 Low
Aging                 Poor
Availability          Poor

Likely MI interpretation:

Primary Constraint: Inventory Mix

The dealership may not have too little inventory. It may have the
wrong inventory.

PART II --- FULFILLMENT & SERVICE SUPPORT

7. Availability vs Fulfillment

Inventory Availability: Did we have the required part?

Fulfillment Performance: If we had the part, how effectively did we
get it to the technician/job?

Conceptual flow:

Part Requested
      ↓
Located / Allocated
      ↓
Issued
      ↓
Delivered / Available to Technician

Potential derived measure: Parts Fulfillment Time.

The architecture supports richer integrations without requiring all
tenants to manually capture every event.

Automate the facts. Infer what can be inferred. Ask humans for
judgment. Capture the decision. Return the manager to the operation.

8. Parts Constraint Types --- FROZEN

Stocking Constraint

Demand occurred for something the operation reasonably should have
stocked.

External Supply Constraint

The part is not reasonably available because of OEM/vendor/backorder
conditions.

Fulfillment Constraint

The part is available but internal Parts process delays getting it to
the job.

Ordering / SOR Constraint

Delay occurs in identification, ordering, receipt, notification, or
installation coordination.

This prevents generic blame and allows MI to recommend the appropriate
intervention.

9. Connection to Domain 4

Parts connects directly to Technician & Capacity:

Parts Availability ↓
        ↓
Parts Requests Delayed
        ↓
Technician Interruption ↑
        ↓
Productivity ↓
        ↓
Proficiency ↓
        ↓
FRH ↓
        ↓
Labor GP Capacity ↓

The Domain 4 distinction remains mandatory:

RO Delay ≠ Technician Lost Time

A vehicle may wait for a part while the technician works productively
elsewhere. MI must distinguish RO cycle-time impact from technician
productive-time impact.

PART III --- SOR & BACKORDER MANAGEMENT

10. SOR Lifecycle --- FROZEN v1

Part Needed
      ↓
Ordered
      ↓
ETA
      ↓
Received
      ↓
Customer / RO Ready
      ↓
Installed / Consumed
      ↓
Closed

Useful underlying measures may include: - Open SOR count and $ - SOR
age - Backordered SOR count and $ - Received-not-installed count and
$ - SORs tied to aging open ROs - SORs past expected ETA - Time from
receipt to installation/consumption - Cancelled / returned SORs

Primary Exception States

1. Ordered / ETA Valid
No intervention. MI monitors silently.

2. Past ETA / Not Received
Determine whether ETA changed, an external supply constraint exists, or
follow-up is required.

3. Received / Not Installed
Potential conversion opportunity requiring attention.

4. No Longer Needed / Unresolved
Potential inventory exposure.

A genuine OEM/vendor backorder is an external supply constraint, not
automatically a Parts Manager performance failure.

Remember the ETA, monitor it, and intervene only when the
expectation fails.

11. Received-Not-Installed Opportunity

Received SOR inventory may represent unusually actionable opportunity
because customer need, repair identification, ordering, and receipt have
already occurred.

MI may elevate material received-not-installed work and estimate
associated Parts and Service GP opportunity.

This is more useful than simply displaying SOR inventory dollars.

PART IV --- FINANCIAL & CHANNEL PERFORMANCE

12. Parts Financial Performance --- FROZEN v1

Canonical measures:

Parts Sales

Parts Cost of Sales

Parts Gross Profit

Parts Gross Margin %

Parts GP = Parts Sales − Parts COS

Parts Margin % = Parts GP ÷ Parts Sales

These measures should exist at total Parts and, where useful, by
channel.

13. Canonical Parts Channels

Default channels:

Service / RO

Wholesale

Retail Counter

Internal

Other

Within Service/RO, source data may further distinguish: - Customer Pay -
Warranty - Internal

14. Parts-to-Labor Ratio

Parts-to-Labor Ratio = Corresponding RO Parts Sales ÷ Corresponding
Labor Sales

The word corresponding is mandatory. Wholesale parts sales should
not be compared with Service labor sales.

Potential views: - CP Parts-to-Labor - Warranty Parts-to-Labor -
Internal Parts-to-Labor - Total RO Parts-to-Labor

MI should not assume a universal ideal ratio because brand, work mix,
labor rates, vehicle age, repair mix, and tenant operating model affect
it.

15. Parts Purchase Incentives / Rebates --- Canonical Correction

Allowance & Discount is an AutoNation-specific accounting term used
for OEM parts bonus monies, purchase rebates, volume incentives, and
similar parts-purchase incentive income.

It should not become the universal canonical term.

Canonical Concept

Parts Purchase Incentives / Rebates

Tenant mapping handles local terminology:

AutoNation "Allowance & Discount"
            ↓
Parts Purchase Incentives / Rebates

MI must distinguish financial improvement created by operating Parts
margin from improvement created by incentive/rebate income.

Subject to tenant accounting structure:

Parts Operating GP
      +
Parts Purchase Incentives / Rebates
      ±
Inventory Adjustments / Other Defined Items
      =
Parts Financial Contribution

16. Inventory Adjustments

Inventory Adjustments remain a distinct concept.

MI should evaluate: - Magnitude - Frequency - Direction - Trend

Persistent negative adjustments may indicate upstream issues involving
receiving, bin accuracy, issuing, returns, physical controls, or process
discipline.

PART V --- MANAGEMENT INTELLIGENCE

17. Parts as Both Cause and Consequence

Parts can be both a downstream financial result and an upstream cause of
Service performance.

Example:

Parts GP Below Objective
        ↓
RO Parts Sales Below Expected
        ↓
Service FRH Below Requirement
        ↓
Technician Productivity Low
        ↓
Waiting for Parts Elevated
        ↓
Inventory Availability Problem

This reinforces the need for a future cross-domain causal map.

18. Example: Inventory Mix Constraint

Evidence:

DSO                      High
Turns                    Low
10–12 Inventory          Increasing
12+ Inventory            Increasing
Recurring Stock-outs     Elevated
Buyouts                  Elevated
Technician Waiting       Elevated

MI should synthesize these into one issue:

Primary Constraint: Inventory Mix

Inventory investment is above expected, but recurring Service demand
is not being satisfied. Excess investment is concentrated in aging
inventory while recurring stock-outs are contributing to technician
lost time and delayed ROs.

Management Attention: Correct identified recurring stocking gaps
and address Freight Train inventory before additional obsolescence is
created.

19. Example: Fulfillment Constraint

If requested parts are in stock, inventory health is normal, internal
fulfillment time is excessive, and technician waiting is elevated:

Primary Constraint: Parts Fulfillment Process

MI should not recommend increasing inventory because the issue is
Process, not Quantity.

20. Parts Through the 4 P's

People

Parts staffing, capability, role structure, accountability.

Platform

Inventory, warehouse, physical layout, systems, DMS, Parts technology.

Process

Stocking, ordering, receiving, picking, issuing, fulfillment, SOR
handling, returns, inventory controls.

Performance

Availability, Turns, DSO, margin, obsolescence, Parts GP, Service
support, technician waiting, RO cycle impact.

21. Domain 5 Manager Experience

The Parts Manager should not begin with a wall of KPIs.

Desired experience:

PARTS --- 2 ITEMS REQUIRE ATTENTION

1. Inventory Mix --- High Impact
Recurring Service stock-outs are occurring despite inventory above
expected levels. Correct identified stocking exceptions and intervene
on 10--12 month Freight Train inventory before additional obsolescence
is created.

2. Received SOR Conversion --- Medium Impact
Received special-order parts remain uninstalled beyond expectation,
representing identifiable Parts and associated Service GP opportunity.

Supporting KPIs, trends, transactions, and calculations remain available
as evidence.

22. Domain 5 Smoke Test

The architecture must answer:

Can MI tell a Parts Manager the one to three things that actually
require management attention without requiring the manager to spend
the day feeding or interpreting ProdTracker?

Domain 5 v1 passes that test.

23. Governing MI Doctrines Now Frozen

4 P's

People → Platform → Process → Performance

Upstream Principle

When Performance deviates from the desired outcome, MI traces the
variance upstream until it identifies the earliest material constraint
management can influence.

Automation Principle

Automate the facts. Infer what can be inferred. Ask humans for
judgment. Capture the decision. Return the manager to the operation.

Management Attention Principle

Complexity belongs in the system. Management receives the fewest
actionable items necessary to materially improve the operation.

24. Session Decisions --- FROZEN

Domain 5 --- Parts Operations v1

Management Attention Principle

Three-level Management Attention / Evidence / Underlying Data
experience

Materiality as a management-attention filter

Inventory Health = Quantity / Velocity / Quality / Availability

DSO

Inventory Turns / velocity

Default aging: 0--4 / 4--6 / 7--9 / 10--12 / 12+

10--12 = Technical Obsolescence / Freight Train

Tenant-configurable aging standards

Aging migration

Legacy vs new obsolescence generation

Fill Rate where supported

Stock-outs

Buyouts / Emergency Purchases

Backorders

Special Orders

Lost Sales

First-Time Fill Rate optional/source-dependent

Stock-out and buyout as separate concepts

Inventory availability vs fulfillment performance

Stocking / External Supply / Fulfillment / Ordering-SOR constraint
classification

RO Delay vs Technician Lost Time retained

SOR lifecycle and exception states

ETA monitoring rather than repetitive explanation

Received-not-installed SOR opportunity

Parts Sales / COS / GP / Margin

Canonical Parts channels

Parts-to-Labor Ratio using corresponding sales

Parts Purchase Incentives / Rebates as canonical concept

AutoNation Allowance & Discount mapped to that canonical concept

Inventory Adjustments maintained separately

Parts treated as both financial engine and Service-production
enabler/constraint

25. Next Session Starting Point

Domain 6 --- Customer / Service Experience

Potential areas:

Customer satisfaction / CSI

Retention

Appointment demand and access

Appointment conversion

No-shows

Communication

Status updates

Promise-time performance

Cycle experience

Customer authorization experience

Comebacks / rework impact

Survey response and measurement limitations

OEM-specific versus tenant-specific experience measures

Guardrails:

Do not create manual workload merely to create a KPI.

Do not confuse an OEM or enterprise-specific score with a universal
automotive concept.

Do not give management ten red metrics when one upstream action
explains them.

Session Closing Principles

Great dealerships are not built by great reports. They are built by
great management decisions, repeated consistently.

MI should always look upstream.

The depth belongs inside MI, not in the manager's workload.

Complexity belongs in the system. Management receives the fewest
actionable items necessary to materially improve the operation.

A dealership can have too much inventory and still not have the
parts it needs. Inventory health is a system, not a single KPI.

At 12+ months, management is dealing with obsolescence. At 10--12
months, management can still see the Freight Train coming.