MI v5 --- Session 0016

Domain 4: Technician & Capacity --- Management Reasoning Architecture

Date: August 9, 2026Project: ProdTracker Management Decision Platform --- ManagementIntelligence v5Status: Architecture / Domain DefinitionSession Outcome: Domain 4 --- Technician & Capacity v1 FROZEN

1. Session Purpose

Complete the canonical architecture for Domain 4 --- Technician &Capacity and formalize several foundational Management Intelligencedoctrines that emerged from the work.

The session moved beyond defining technician KPIs. It established how MIshould reason from financial requirements backward into staffing,capability, work mix, operating flow, and management intervention.

A central principle emerged:

MI should always look upstream.

Performance is the downstream result. Management Intelligence shouldidentify the upstream conditions that produced it.

2. Foundational MI Management Model --- The 4 P's

The operating framework is:

People → Platform → Process → Performance

These are not four independent categories. They form a causal managementchain.

People

Do we have: - The right people? - The right number of people? - Theright capability mix? - The right organizational structure? -Sustainable distribution of production? - Appropriate development andsuccession capacity?

Platform

Does the operating environment support the objective?

Platform includes: - Facility - Productive bays - Equipment -Technology - Systems - Organizational infrastructure - Physicalproductive capacity

Process

Do operating processes consistently convert People and Platform intoproductive work?

Examples include: - Scheduling - Dispatch - Route-sheet management -Parts availability - Customer authorization - MPI execution - Workassignment - Technician start/stop behavior - Workflow - Communication -Aging RO management

Performance

Are People, Platform, and Process producing the intended operational andfinancial outcomes?

Examples include: - FRH - ELR - Labor sales - Gross margin - GP / RO -Total Gross Profit - Budget / YoY / tenant-target attainment

Performance is the consequence of the first three P's, not merelysomething management demands.

3. MI Upstream Principle

Formal Principle

When Performance deviates from the desired outcome, ManagementIntelligence should trace the variance upstream through its measurabledrivers and operating conditions until it identifies the earliestmaterial constraint management can influence.

MI should not stop at:

"Performance is below target."

It should ask:

What upstream condition produced the performance?

Example:

GP below target
        ↑
FRH below requirement
        ↑
Proficiency below requirement
        ↑
Productivity is the constraint
        ↑
Technician productive time is being lost
        ↑
Route-sheet dispositions show Waiting for Parts
        ↑
Primary upstream constraint = Parts Process

The purpose is not to generate a long list of imperfect metrics. Thepurpose is to identify the highest-leverage controllable constraint.

Reporting explains the result. Management Intelligence identifieswhat management should change.

4. MI Automation Principle

A second foundational doctrine was formalized:

Management Intelligence should consume operational dataautomatically wherever possible and require human input primarily forjudgment, decisions, exceptions, and commitments.

The preferred information hierarchy is:

System-derived first

MI-inferred second

Human-confirmed where judgment matters

Manual entry only when information cannot reasonably be obtainedelsewhere

Examples of system-derived data: - DMS transactions - Repair orders -Technician punches - FRH - ELR - Financial data - Opcode data -Appointments - Training records - OEM data - MPI data

Examples of MI-inferred information: - Proficiency - Work-mix patterns -Capability patterns - Dependency - Likely constraints - Classificationreview suggestions - Trends

Examples requiring human judgment: - Assigned technician skill level -Exception explanation - Management agreement - Management decision -Owner - Expected outcome - Commitment

Automation Doctrine

Automate the facts. Infer what can be inferred. Ask humans forjudgment. Capture the decision. Return the manager to the operation.

A manager should not spend the day maintaining ProdTracker.

The ideal MI experience is:

"The system already understands what happened. I need to decide whatwe are going to do about it."

5. Structural Technician Capacity --- Backward from the Economic Requirement

Required technician staffing should not begin with an arbitrary FRHtarget or bay count.

The economic objective should determine the production requirement.

The target basis is tenant-configurable:

Budget

YoY

Tenant Target

Example

Total Aftersales GP Objective             $300,000

Less:
Expected Parts GP                        (135,000)
Expected Sublet / Other GP                (10,000)
                                         ---------
Required Labor Contribution               155,000

Add:
Unapplied Labor Expense to Recover         20,000
                                         ---------
Required Applied Labor GP                $175,000

If expected labor margin is 75%:

Required Labor Sales
$175,000 ÷ 75%
= $233,333

If expected ELR is $183:

Required FRH
$233,333 ÷ $183
≈ 1,275 FRH

The financial objective therefore determines the required FRH.

6. Required Technician FTE --- 100% Proficiency Baseline

Required structural staffing should be calculated at 100%Proficiency.

Example:

Required FRH              1,275
Hours / Day                   8
Working Days                  22

Monthly Hours / FTE          176

Required FTE
1,275 ÷ 176
= 7.24

Operational requirement:

8 productive technician FTE

Frozen Principle

Required Technician FTE is calculated at 100% Proficiency.Proficiency above 100% represents performance leverage and should notbe used to reduce the structural staffing requirement.

This supports the dependency-flattening philosophy being developed inthe book.

If required staffing is reduced because a few technicians routinelyproduce 125%--140% proficiency, the organization becomes structurallydependent on exceptional individual production.

That is not sustainable capacity. It is dependency.

Structural Capacity vs Expected Production

Structural Requirement

Required FTE based on 100% Proficiency

Expected Production

Staffed technician hours × expected/current Proficiency

These answer different questions:

How many technicians should the business structurally require?

versus:

Given the technicians currently staffed and their performance, whatare they likely to produce?

7. Dependency Flattening

The 100% Proficiency staffing baseline supports a broader managementprinciple:

Do not capitalize exceptional individual performance into theminimum staffing requirement.

Performance above 100% should provide: - Growth capacity - Resilience -Workload flexibility - Training capacity - Succession capacity - Reducedindividual dependency - Additional production leverage

A shop can achieve budget while remaining structurally unhealthy if toomuch required production depends on a small number of exceptionaltechnicians.

This is where proprietary intelligence such as UVI and TSIbecomes important.

Achieving the performance result does not prove the operating systemis healthy.

8. Calendar Utilization --- FROZEN v1

Calendar Utilization measures workforce availability against the plannedworking calendar.

Formula

Calendar Utilization % = Calendar-Available Scheduled Hours ÷ PlannedWorking Hours

Planned Working Hours exclude recognized closed holidays.

Calendar-based losses include: - PTO - Training - Sick time - Leave -Other legitimate absence categories

Vacancies do not belong in Calendar Utilization.

Overtime should be tracked as additional capacity rather than used toartificially restore Calendar Utilization.

Management Meaning

Was the employed technician workforce available according to plan?

9. Facility Utilization --- FROZEN v1

Facility Utilization measures the use of physical service-bay capacity.

Formula

Facility Utilization % = Total Productive / Billable Hours ÷ TotalAvailable Bay Hours × 100

Available Bay Hours

Available Bay Hours = Productive Bays × Operating Hours × OperatingDays

Facility Utilization measures the asset, not workforce staffing.

Management Meaning

Are we converting available physical bay capacity into productiveoutput?

10. Productivity, Efficiency, and Proficiency --- FROZEN v1

The traditional fixed-operations distinction among these three measuresis restored.

Productivity

Productivity measures technician time actually spent working.

Productivity = Actual Working Time ÷ Available Technician Time

Example:

Available Time        8.0 hours
Actual Working Time   6.0 hours

Productivity = 75%

Efficiency

Efficiency measures how efficiently the technician performs theassigned work.

Efficiency = FRH / Expected Job Hours ÷ Actual Working Time

Example:

Job pays / flags      2.0 hours
Actual working time   1.0 hour

Efficiency = 200%

Efficiency evaluates job execution, not the technician's entire day.

Proficiency

Proficiency measures FRH production versus total technician time andprovides the clearest top-level picture of technician effectiveness.

Proficiency = Total FRH Produced ÷ Available Technician Time

Example:

Available Time     8.0 hours
FRH Produced      10.0 hours

Proficiency = 125%

Mathematical Relationship

Proficiency = Productivity × Efficiency

Example:

Productivity = 62.5%
Efficiency   = 200%

Proficiency  = 125%

Management Hierarchy

Proficiency is the top-level technician-effectiveness outcome.

Productivity and Efficiency are diagnostic drivers explainingProficiency.

11. Technician Capability Taxonomy --- FROZEN v1

MI will use the tried-and-true fixed-operations A/B/C/D techniciantaxonomy.

The classification is tenant-assigned.

A --- Master Technician

Highest technical capability.

Typical characteristics: - Advanced diagnosis - Complex repair -Advanced electrical / drivability - Difficult intermittent concerns -Broad technical capability - Can effectively "clean the ticket"

B --- Journey-Level Technician

Experienced and broadly capable.

Typical characteristics: - Several years of experience - Multiple ASEcertifications - Manufacturer training - Broad mechanical and repaircapability - Can clean most of the ticket - May not yet independentlyhandle the most advanced diagnostic work

C --- Line / Developing Technician

Developing repair technician.

Typical characteristics: - Approximately 1--5 years depending ondevelopment - Maintenance - Light mechanical work - General repair -Building experience and training - Developing diagnostic capability

D --- Entry / Express Technician

Beginning productive technician.

Typical characteristics: - Express service - PDI - Basic maintenance -Low-level mechanical work - Early development stage

12. Tenant-Authoritative, MI-Assisted Classification

The tenant remains authoritative for A/B/C/D assignment.

MI may recommend review when objective evidence materially differs fromthe assigned classification.

Example:

Assigned Skill Level: C
Experience: 5 years
ASE: 8 certifications
Manufacturer Training: substantial
Demonstrated Work: B-level

MI may ask:

"This technician is currently classified C. Their capabilityevidence appears more consistent with B-level work. Is C still theappropriate classification?"

The manager may: - Keep C - Change to B - Review later

MI should never silently reclassify a technician.

Two Capability Concepts

Assigned Skill LevelTenant-authoritative A/B/C/D classification.

Inferred Capability LevelMI's evidence-based assessment.

The gap between the two becomes intelligence.

Frozen Principle

Credentials indicate potential capability. Demonstrated performancevalidates capability.

Supporting evidence may include: - Experience - ASE certifications -Manufacturer certifications - Training - Work performed - Jobcomplexity - Efficiency by work type - Diagnostic performance - Comeback/ rework - Production history

13. Technician Capability and Work-Mix Alignment

Low-producing technicians are not automatically underperformingtechnicians.

A technician may have: - Limited current capability - Insufficienttraining - Limited experience - Poor work allocation - Insufficientappropriate work - A work-mix mismatch

Capability Envelope

Capability envelope means the range of work a technician cancurrently perform competently and independently.

MI should evaluate performance within that context.

Low production alone is insufficient evidence of poor technicianperformance.

14. Work-Mix Classification --- FROZEN CONCEPT

Work Mix should describe the capability required to perform work, notmerely the opcode or repair category.

The work classification will conceptually align with A/B/C/D techniciancapability.

Examples:

A-Level Work

Advanced diagnostic

Complex electrical

Network diagnosis

Difficult intermittent concerns

Highly complex repair

B-Level Work

Journey-level mechanical repair

Major repair

Suspension

Engine / transmission work

Moderate diagnostic work

Complex warranty work

C-Level Work

Brakes

Tires

Alignments

Batteries

Scheduled maintenance

Light mechanical repair

D-Level Work

Oil service

Tire rotation

PDI

Basic maintenance

Express work

These examples are guidance, not universal hard-coded truth.

The tenant may map its own operations and opcodes.

15. Hierarchical Skill-to-Work Matching

The capability relationship is hierarchical:

A technician → A / B / C / D work
B technician → B / C / D work
C technician → C / D work
D technician → D work

An A technician performing C-level work is not automatically a problem.

MI should detect structural patterns of scarce-capabilityconsumption.

Example:

A-level technicians consistently spend significant productive timeperforming C/D work while C/D technicians have unused capacity andadvanced work is aging.

That is a work-allocation problem, not an individual technicianproblem.

16. Work-Mix Development as a Capacity Strategy

Maintenance and competitive-service sales are not merely revenueopportunities.

They can also be work-mix creation mechanisms.

Examples: - Maintenance - Tires - Brakes - Alignments - Batteries -Express services - Other legitimate competitive-service work

Increasing appropriate work can:

Increase developing-technician production

Improve Productivity

Release advanced-technician capacity

Flatten production dependency

Improve labor cost structure

Improve labor margin

Increase total productive capacity

Improve total Gross Profit potential

Economic Flywheel

Better Work Mix
        ↓
Better Skill-to-Work Matching
        ↓
Higher Developing-Tech Production
        ↓
Advanced-Tech Capacity Released
        ↓
Greater Total Shop Capacity
        ↓
Lower Production Dependency
        ↓
Healthier Cost Structure
        ↓
Improved Margin
        ↓
Higher GP Capacity

Frozen Principle

Technician development and work-mix development are complementarystrategies. Management should both increase employee capability overtime and create an appropriate mix of work that allows the existingworkforce to contribute productively today.

17. Capability / Work-Mix Mismatch

A shop may have: - Enough technicians - Enough total work - HealthyCalendar Utilization

and still miss FRH because:

The work and the workforce do not fit each other.

MI must therefore be capable of identifying:

Primary Constraint: Capability / Work-Mix Mismatch

Potential evidence:

Developing technicians have unused productive capacity

Advanced technicians carry excessive production concentration

Appropriate C/D work is insufficient

Advanced work is aging

Work is routed to capability levels inefficiently

18. Route Sheet / Flow Intelligence --- FROZEN v1

ProdTracker should not recreate the entire DMS route sheet.

MI needs the events necessary to understand operational flow andmaterial exceptions.

Minimum Canonical Flow States

Work Available
      ↓
Routed
      ↓
Started
      ↓
Working
      ↓
Interrupted / Waiting
      ↓
Resumed
      ↓
Completed
      ↓
RO Closed

Where source systems provide the data, MI should automatically captureor derive timestamps for:

RO Open

Work Available

Work Routed

Technician Start

Technician Stop / Pause

Technician Resume

Work Complete

RO Complete

RO Closed

Derived Durations

MI may derive: - Time to Route - Time to Start - Actual Working Time -Interrupted / Waiting Time - Time to Complete - Completed-to-CloseTime - Total RO Cycle Time

19. RO Delay vs Technician Lost Time

This distinction is mandatory.

RO Delay ≠ Technician Lost Time

Example:

A vehicle may wait five days for a backordered part.

That increases: - RO Age - RO Cycle Time

But if the technician works productively on other vehicles, it doesnot necessarily reduce technician Productivity.

MI must preserve both concepts separately.

20. Canonical Disposition Taxonomy

Dispositions explain material delays and lost productive capacity.

Canonical parent categories:

Waiting for Work / Dispatch

Waiting for Parts

Waiting for Authorization

Technical / Diagnostic

Warranty / OEM Approval

Sublet

Vehicle / Customer Constraint

Facility / Equipment

Rework / Comeback

Other

Tenants may define more granular child reasons while MI retainscanonical parent categories for cross-organization reasoning.

Upstream Interpretation

Waiting for Work / DispatchPotential scheduling, demand, routing, or dispatch constraint.

Waiting for PartsPotential Parts / process constraint.

Waiting for AuthorizationPotential ASM / customer communication constraint.

Technical / DiagnosticPotential capability, support, equipment, or work-assignment constraint.

Facility / EquipmentPotential Platform constraint.

Rework / ComebackPotential quality, Process, or capability constraint.

21. Aging RO Intervention --- FROZEN v1

RO aging should become an active management-control process rather thana retrospective aging report.

Aging Threshold

A tenant-configurable aging threshold triggers intervention.

A default such as 3 days may be offered, but the tenant owns thestandard.

Once the threshold is crossed:

An aging RO becomes a management exception requiring an expecteddisposition and completion plan.

Workflow

Aging Threshold Crossed
        ↓
ASM Disposition / Explanation
        ↓
Expected Completion / Close
        ↓
Manager Agrees or Intervenes
        ↓
MI Monitors Commitment
        ↓
Reintervention only if plan fails
or conditions materially change

Automation Rule

The ASM should not repeatedly explain the same known condition.

If:

Waiting for Parts
ETA: 8/12
Expected Close: 8/13
Manager Reviewed

MI should remember that plan and monitor it.

The issue resurfaces only if: - Expected completion passes - Dispositionchanges - Source data contradicts the plan - A new material exceptionappears

Frozen Principle

Ask once. Remember the answer. Ask again only when realitychanges.

22. Aging Priority

Age alone should not determine management priority.

Age + disposition + expectation + adherence to expectation determinemanagement priority.

Example:

RO A
6 days old
Parts ETA documented
Manager reviewed
Expected close still valid
→ Plan Healthy

RO B
4 days old
No disposition
No expected completion
→ Management Intervention Required

RO C
8 days old
Expected close date missed
→ Reintervention Required

The older RO is not automatically the most important management issue.

23. Institutional Management Memory

Exception data should aggregate over time.

Example:

Waiting for Parts represents 38% of >3-day ROs and 46% of technicianinterruption time.

MI should then stop treating these as isolated aging ROs and recognize asystemic upstream constraint.

Other examples:

Authorization delays concentrated with one ASM

Diagnostic aging concentrated among certain capability levels

Facility constraints recurring during specific periods

Work-mix mismatch producing persistent developing-technician idletime

This begins converting operating history into institutional managementmemory.

24. Domain 4 Canonical Architecture

TECHNICIAN & CAPACITY
│
├── STRUCTURAL CAPACITY
│   ├── Technician Headcount
│   ├── Technician FTE
│   ├── Required Technician FTE
│   ├── Staffed Technician FTE
│   └── Technician Capacity Gap
│
├── CALENDAR CAPACITY
│   ├── Planned Working Hours
│   ├── Calendar-Available Hours
│   └── Calendar Utilization %
│
├── FACILITY CAPACITY
│   ├── Productive Bays
│   ├── Available Bay Hours
│   ├── Produced / Billable Hours
│   └── Facility Utilization %
│
├── TECHNICIAN PERFORMANCE
│   ├── Available Technician Time
│   ├── Actual Working Time
│   ├── FRH / Produced Hours
│   ├── Productivity %
│   ├── Efficiency %
│   └── Proficiency %
│
├── TECHNICIAN CAPABILITY
│   ├── Assigned A / B / C / D
│   ├── Supporting Evidence
│   ├── MI Inferred Capability
│   └── Capability Review
│
├── WORK-MIX ALIGNMENT
│   ├── Work Capability Classification
│   ├── Skill-to-Work Matching
│   ├── Scarce-Capability Consumption
│   └── Capability / Work-Mix Mismatch
│
├── ROUTE / FLOW INTELLIGENCE
│   ├── Work Available
│   ├── Routed
│   ├── Started
│   ├── Working
│   ├── Interrupted / Waiting
│   ├── Resumed
│   ├── Completed
│   └── RO Closed
│
├── EXCEPTION / DISPOSITION
│   ├── Canonical Dispositions
│   ├── Technician Lost Time
│   ├── RO Delay
│   └── Aging Intervention
│
└── MI INTELLIGENCE
    ├── UVI
    ├── TSI
    ├── Dependency Analysis
    ├── Capability / Work-Mix Analysis
    ├── Constraint Identification
    └── Upstream Management Recommendation

25. Canonical vs Proprietary Intelligence

Canonical automotive data describes the operation.

Examples: - Technician FTE - Available Hours - Actual Working Time -FRH - Productivity - Efficiency - Proficiency - Facility Utilization -Calendar Utilization - Skill Level - Work Mix - Route Events -Dispositions

The proprietary MI intelligence layer evaluates those facts.

Examples: - UVI - TSI - Dependency analysis - Capability mismatch -Constraint identification - Sustainability - Management recommendation -Decision history

The canonical layer describes reality. The proprietary intelligencelayer determines what that reality means for management.

26. MI Architecture Emerging from the Work

Three broad layers are now visible.

Layer 1 --- Canonical Automotive Model

Defines what exists and what the metrics mean.

Layer 2 --- Management Reasoning Model

Includes: - 4 P's - Upstream Principle - Decomposition relationships -Causal relationships - Automation Principle

Layer 3 --- Proprietary Intelligence

Includes: - UVI - TSI - Dependency analysis - Constraintidentification - Management attention - Decision history - Patternrecognition

AI operates across these layers rather than being expected to improvisedealership management from raw data.

Emerging Product Architecture

Canonical data tells MI what exists.The 4 P's tell MI where to look.The Upstream Principle tells MI which direction to reason.Proprietary intelligence tells MI what matters.AI enables MI to reason and communicate across all of it.

27. Vocabulary Added

Ontology

Pronunciation: on-TOL-uh-jee

In this context:

A formal model of what things exist in a domain and how those thingsrelate to one another.

The KPI taxonomy organizes measurements.

The broader automotive management ontology connects: - Technicians -Bays - ROs - FRH - Departments - Processes - Financial outcomes -Constraints - Capabilities - Decisions

Capability Envelope

The range of work a person can currently perform competently andindependently.

Decomposition

Breaking a complex result into contributing components so managementcan understand what produced it.

28. Domain 4 Smoke Test

No material contradiction was identified.

The architecture connects cleanly:

Financial requirement determines structural capacity. Capability andwork mix determine whether that capacity is properly configured.Calendar, Facility, Productivity, Efficiency, and Proficiency explainhow capacity is being used. Route-sheet and disposition data explainwhy gaps exist. MI then looks upstream and directs managementattention.

29. Session Decisions --- FROZEN

Domain 4 --- Technician & Capacity v1

4 P's management reasoning framework

MI Upstream Principle

MI Automation Principle

Backward technician-capacity calculation from Aftersales GPobjective

Budget / YoY / Tenant Target as configurable objective basis

Required Technician FTE based on 100% Proficiency

Proficiency above 100% treated as performance leverage

Dependency-flattening principle

Calendar Utilization definition

Facility Utilization definition

Productivity definition

Efficiency definition

Proficiency definition

Proficiency = Productivity × Efficiency

A/B/C/D technician capability taxonomy

Tenant-authoritative, MI-assisted classification

Capability evidence and review concept

Work-Mix Classification concept

Hierarchical skill-to-work matching

Capability / Work-Mix Mismatch

Route Sheet / Flow Intelligence

RO Delay vs Technician Lost Time

Canonical disposition taxonomy

Aging RO intervention workflow

Commitment monitoring rather than repetitive explanation

30. Next Session Starting Point

Proceed to:

Domain 5 --- Parts Operations

Parts must be evaluated in at least two roles:

Financial engine

Upstream operational constraint / enabler of Service production

Initial questions should include: - Parts sales - Parts gross profit -Parts margin - Parts-to-labor relationship - Inventory productivity -Fill rate / availability - Special-order parts - Obsolescence -Inventory adjustment - Allowances / discounts - Wholesale vs Retail /Service RO parts - Parts delays as a Service Productivity and RO-cycleconstraint

Domain 5 should preserve the same design doctrines established in thissession:

People → Platform → Process → Performance

MI should always look upstream.

Automate the facts. Infer what can be inferred. Ask humans forjudgment. Capture the decision. Return the manager to the operation.

Session Closing Principles

Great dealerships are not built by great reports. They are built bygreat management decisions, repeated consistently.

Achieving the performance result does not prove the operating systemis healthy.

Build People capacity for sustainable performance. Do not design theorganization around exceptional overperformance.

Low production alone is insufficient evidence of poor technicianperformance.

The KPI tells us what happened. The operating system tells us why.MI should look upstream until it finds what management can change.

Automate observation so management can spend its time onintervention.