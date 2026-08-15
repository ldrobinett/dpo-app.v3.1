MI v5 --- Session 0015

Canonical KPI Taxonomy and Technician Capacity

Date: August 8, 2026Project: ProdTracker Management Decision Platform --- ManagementIntelligence v5Status: Architecture / Domain Definition

1. Session Purpose

Continue defining the canonical automotive KPI taxonomy for ManagementIntelligence v5. The system must fit both large enterprise dealer groupsand a single dealership with a small team. Canonical KPIs thereforerepresent durable automotive concepts rather than one company'sscorecard.

Canonical: the standard, authoritative form of a concept inside MI.Taxonomy: a structured system for organizing concepts into logicalcategories and relationships.

The taxonomy is not merely a KPI list. It tells MI what a number means,where it belongs, what relates to it, and how it should be interpreted.

2. Canonical and Tenant-Specific KPIs

MI will support two complementary layers.

Automotive Canonical KPIs

Durable automotive measures understood consistently across tenants, suchas Gross Profit, RO Count, VIN Count, Hours/RO, ELR, Productivity,Efficiency, and Proficiency.

Tenant-Specific KPIs

Organizations may define KPIs required by their own scorecards,manufacturer programs, or operating systems without changing the meaningof the canonical model.

3. KPI Dictionary Requirement

Every metric in MI must be capable of explaining itself.

The Help area will include a KPI Dictionary. Each metric shouldultimately know its name, definition, formula, origin, management type,unit, dimensions, valid denominator/population, desired direction whereapplicable, related drivers/outcomes/results, plain-language "why itmatters," and tenant ownership when tenant-defined.

The dictionary should be generated from metric definitions rather thanmaintained as disconnected documentation.

4. Domain 1 --- Financial Performance

STATUS: FROZEN v1

Canonical financial concepts: - Revenue - Gross Profit - OperatingExpense - Operating Profit - Gross Margin % - Service Absorption %

Financial metrics are canonical concepts. Automotive business areas anddimensions explain where results were produced: New Vehicle, UsedVehicle, F&I, Service, Parts, Collision, pay type, channel, store,group/market, enterprise, and time period.

Do not create a new KPI merely because the same business measure isviewed from a different place, category, time period, or comparison.

5. Domain 2 --- Customer & Vehicle Volume

STATUS: Substantially defined; final freeze pending.

The domain must distinguish transaction count, vehicle occurrence count,and unique population count.

Current structure: - Demand: Appointments; Service Contacts placementstill under consideration - Visit / Vehicle: Vehicle Arrivals; VINCount - Transaction: Repair Orders Opened; Repair Orders Closed -Population / Retention: Unique Customers; Unique VINs

VIN Count Correction

VIN Count is not unique VIN population. If the same physical VIN hasthree qualifying service visits in August:

Repair Orders         3
VIN Count             3
Unique Physical VINs  1

Working canonical definition:

VIN Count: The count of qualifying vehicle service occurrencesduring the reporting period, with a VIN counted once for eachqualifying service event.

RO Count, VIN Count, and Unique VIN Count answer different questions andmust not be substituted merely because a source system makes one easierto obtain.

6. Domain 3 --- Service Sales & Production

STATUS: FROZEN v1

Fundamental measures: - Labor Hours Sold - Labor Sales - Parts Sales -Labor Cost - Parts Cost - Door Labor Rate

Derived measures:

ELR = Labor Sales ÷ Labor Hours Sold

ELR % of Door Rate = ELR ÷ Door Labor Rate × 100

ELR realization must be analyzable by labor type.

Hours / RO = Labor Hours Sold ÷ Qualifying RO Count

Labor Sales / RO = Labor Sales ÷ Qualifying RO Count

Parts Sales / RO = Parts Sales ÷ Qualifying RO Count

Average RO Sales = Qualifying RO Sales ÷ Qualifying RO Count

Average RO Sales remains distinct from GP / RO.

Labor Gross Margin % = Labor Gross Profit ÷ Labor Sales

Parts Gross Margin % = Parts Gross Profit ÷ Parts Sales

Parts-to-Labor Ratio = Parts Sales ÷ Labor Sales

Parts-to-Labor is diagnostic. A larger ratio is not automaticallybetter.

Gross Profit / RO = Qualifying Gross Profit ÷ Qualifying RO Count

Every per-RO measure must explicitly identify its qualifying ROpopulation.

7. GP / RO Decomposition

Decomposition: breaking a complex result into contributing parts somanagement can understand what produced it.

MI should understand the economic chain beneath GP / RO:

Door Rate → ELR → ELR Realization
                 ↓
              Hours / RO
                 ↓
             Labor $ / RO
                 +
             Parts $ / RO
                 ↓
           Average RO Sales
                 ↓
      Labor Margin + Parts Margin
                 ↓
               GP / RO
                 ↓
        RO Volume × GP / RO
                 ↓
         Service Gross Profit

MI should eventually determine whether a GP / RO gap is primarilyattributable to Hours / RO, ELR realization, labor margin, parts margin,parts sales, parts-to-labor mix, or a combination.

8. Domain 4 --- Technician & Capacity

STATUS: IN DEVELOPMENT --- NOT FROZEN

A core objective is to restore the proper distinction amongProductivity, Efficiency, and Proficiency.

The automotive industry has often used these familiar termsinconsistently. MI will use internally consistent canonical definitionsand map source-system terminology into them.

9. Three Technician Time States

AVAILABLE / CLOCKED TIME
Technician capacity available to the operation
            ↓
ACTUAL WORKING TIME
Time actually spent performing vehicle work
            ↓
FLAGGED / PRODUCED HOURS
Credited production generated by that work

MI must understand actual working time on the vehicle/job, notmerely attendance/clocked time and flagged hours.

Actual working time must be represented as underlying data whereversource systems provide it. MI should not silently substitute anothermeasure when it is unavailable.

10. Technician Productivity

Productivity measures how much of the technician's available timewas actually spent working on vehicles.

Productivity = Actual Working Time ÷ Available Time

Example:

Available Time        8.0 hours
Actual Working Time   6.0 hours
Productivity          75%

Productivity is strongly influenced by the operating system: workavailability, dispatch, parts, authorization, vehicle movement,scheduling, equipment, bays, and workflow. Low productivity is notautomatically a technician problem.

11. Technician Efficiency

Efficiency measures how effectively the technician performs workcompared with the expected time required to complete that work.

Efficiency = Expected / Flagged Hours ÷ Actual Working Time

Example:

Expected / Flagged Time   2.0 hours
Actual Working Time       1.0 hour
Efficiency                200%

Efficiency evaluates execution while work is actually being performed.

12. Technician Proficiency

Proficiency measures total credited production generated fromtechnician time available to the operation.

Proficiency = Flagged / Produced Hours ÷ Available Time

Example:

Available Time     8.0 hours
Flagged Hours     10.0 hours
Proficiency       125%

13. Productivity × Efficiency = Proficiency

Example:

Available Time        8 hours
Actual Working Time   5 hours
Flagged Hours        10 hours

Productivity = 5 ÷ 8  = 62.5%
Efficiency   = 10 ÷ 5 = 200.0%
Proficiency  = 10 ÷ 8 = 125.0%

Therefore:

Proficiency = Productivity × Efficiency

This gives MI a diagnostic tree. Low proficiency can be decomposed intolow productivity, low efficiency, or both.

14. Calendar Utilization

Calendar Utilization is separate from technician Productivity.

PTO and training affect calendar utilization rather than being casuallymixed into operating productivity. Holidays are calendar structure andshould be treated as holidays rather than making the operation appearinefficient.

Working concept:

Calendar Utilization measures how much scheduled workforce capacityis actually available after legitimate calendar-based availabilitylosses.

Exact canonical formula remains open.

15. Facility Utilization

Vacancies relate to Facility Utilization, not Calendar Utilization.

Facility Utilization addresses whether the physical productive capacityof the shop is appropriately staffed and usable.

Potential concepts: - Productive Bays / Stations - Facility ProductiveCapacity - Staffed Productive Capacity - Facility Utilization %

Exact canonical definition remains open.

16. Route Sheet and Disposition

The route sheet is where technician productivity becomesoperationally explainable.

If Productivity = Actual Working Time ÷ Available Time, then the gapbetween available time and actual working time represents lost or unusedproductive capacity.

Example:

Available Time        8.0 hours
Actual Working Time   5.5 hours
Productivity Gap      2.5 hours

The useful management question is not merely, "Why is productivity68.8%?" It is:

What happened to the other 2.5 hours?

Potential dispositions: - No work available - Waiting for dispatch -Waiting for parts - Waiting for customer authorization - Vehicleunavailable - Diagnostic assistance - Equipment constraint - Bayconstraint - Rework - Training - Other tenant-defined reason

17. Lost Capacity Attribution

Every material gap between available technician time and actualworking time should be attributable to a disposition whenever thesource data allows it.

Disposition also begins to identify organizational ownership. Waitingfor parts may indicate a Parts/process constraint. No work routed mayindicate dispatch, scheduling, or demand. Waiting for authorization mayindicate an advisor/customer-process constraint. Diagnostic assistancemay indicate a skill/capability constraint. Bay unavailable may indicatea facility constraint.

18. Route Sheet Intelligence Chain

Available Technician Time
          ↓
      Work Routed
          ↓
  Technician Starts Work
          ↓
   Actual Working Time
          ↓
    Work Interrupted?
      ↙         ↘
    No           Yes
    ↓             ↓
 Complete     Disposition
    ↓             ↓
Flag Hours    Lost / Delayed Capacity

The KPI tells us what happened.The route sheet tells us where it happened.Disposition tells us why it happened.MI tells the manager what deserves attention.

This is a foundational product concept.

19. UVI and TSI Positioning

UVI and TSI are not canonical automotive KPIs. They belong to theproprietary MI intelligence layer built on canonical automotive data.

Canonical technician data provides capacity, available time, actualworking time, produced hours, Productivity, Efficiency, and Proficiency.

The MI intelligence layer then uses those facts for measures such as: -UVI - TSI

The canonical layer describes the operation. The proprietaryintelligence layer evaluates concentration risk, workforcesustainability, future capacity risk, and management implications.

20. Current Domain 4 Working Taxonomy

TECHNICIAN & CAPACITY
│
├── WORKFORCE CAPACITY
│   ├── Technician Headcount
│   ├── Technician FTE
│   ├── Scheduled Hours
│   ├── Available Hours
│   └── Calendar Utilization %
│
├── FACILITY CAPACITY
│   ├── Productive Bays / Stations
│   ├── Facility Productive Capacity
│   └── Facility Utilization %
│
├── TECHNICIAN PERFORMANCE
│   ├── Actual Working Time
│   ├── Flagged / Produced Hours
│   ├── Productivity %
│   ├── Efficiency %
│   └── Proficiency %
│
├── ROUTE / FLOW INTELLIGENCE
│   ├── Routed Work
│   ├── Work Start / Stop Events
│   ├── Productivity Gap
│   └── Dispositions
│
└── MI INTELLIGENCE
    ├── UVI
    └── TSI

21. Scalability Principle Reaffirmed

The model must support sophisticated enterprise organizations withoutforcing unnecessary organizational complexity on small dealerships.

Complexity should be available when needed, not mandatory merely becausethe software supports it.

22. Status at End of Session

Frozen

Domain 1 --- Financial Performance v1

Domain 3 --- Service Sales & Production v1

Canonical automotive KPIs remain distinct from tenant-specific KPIs

Every metric must be capable of explaining itself

KPI definitions should power the Help / KPI Dictionary

Dimensions provide context rather than creating duplicate KPIs

Actual working time is required for canonical technicianProductivity and Efficiency

Productivity, Efficiency, and Proficiency are separate concepts

Proficiency = Productivity × Efficiency

Route-sheet disposition explains productivity loss

UVI and TSI belong to the MI intelligence layer

Still Open

Domain 2 --- Customer & Vehicle Volume: final treatment of ServiceContacts / Appointments before formal freeze.

Domain 4 --- Technician & Capacity: 1. Finalize Calendar Utilization2. Finalize Facility Utilization 3. Define productive facility capacity4. Define route-sheet event requirements 5. Define disposition taxonomyand tenant extensibility 6. Confirm canonical technician time-event datarequirements 7. Freeze Domain 4 only after these definitions are precise

23. Next Session Starting Point

Resume at Domain 4 --- Technician & Capacity.

Start with:

Calendar Utilization vs Facility Utilization: precisely define thenumerator, denominator, exclusions, and management meaning of each.

Then complete the route-sheet / disposition architecture and freezeDomain 4.

Session Closing Principles

Great dealerships are not built by great reports. They are built bygreat management decisions, repeated consistently.

The KPI tells us what happened. The route sheet tells us where ithappened. Disposition tells us why it happened. MI tells the managerwhat deserves attention.