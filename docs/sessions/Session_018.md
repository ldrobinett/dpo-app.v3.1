mb seattle.xlsx
Spreadsheet
take a look at this calculator i made for mb seattle.. thoughts? 

The calculator is conceptually strong. It does what most dealership reports fail to do: it connects staffing and facility capacity to gross-profit potential instead of merely reporting last month’s wreckage.

The executive story is already visible:

Current target: $2.001 million
Modeled Facility Gross Potential: $2.604 million
Potential versus target: 130.1%
Current target equals only 42.7% of absolute facility capacity
Modeled FGP captures 55.6% of absolute capacity

That supports a compelling MB Seattle message:

The facility has sufficient physical capacity. The limiting factors are technician staffing, utilization, proficiency, and the operational ability to convert capacity into gross.

What works well
1. It separates physical capacity from practical production

You distinguish:

Facility Potential: 14,400 FRH
True Potential: 6,800.6 FRH
Facility GP Potential: $2.604 million

That is exactly the right structure. Bays tell you what the building could theoretically handle. Technician count and operating assumptions tell you what it can reasonably produce now.

2. The scenario column is useful

Allowing someone to change:

Technician count
Calendar utilization
ELR
Labor and parts margins
Parts-to-labor ratio
Proficiency

makes this a legitimate scenario builder, rather than a decorated multiplication table.

3. It translates operations into money

The model connects FRH to:

Service gross
Parts gross
Total facility gross
Required car count

That makes it useful to a GM or dealer principal, not just a service director who enjoys staring at labor reports until the numbers confess.

Corrections I would make
1. The appointment-needed formula is understated

Your current formula is effectively:

Required cars × 115% × 75%

That reduces the appointment need for a 75% show rate. It should do the opposite.

The proper structure is:

Appointments Needed = Required Repair Orders ÷ Show Rate × Scheduling Buffer

Using your current numbers:

CP car count: approximately 53
Warranty car count: approximately 39
Total required cars: approximately 92
At a 75% show rate: 92 ÷ 75% = 123
With a 15% buffer: approximately 141 appointments

Your sheet currently calculates 79, which is materially too low.

2. Internal-pay volume is not included

You have an IP Mix of 15%, but the car-count calculation only includes CP and warranty.

The calculator needs:

CP Hours/RO
Warranty Hours/RO
Internal Hours/RO
CP car count
Warranty car count
Internal car count
Total daily RO requirement

Right now, 15% of the proposed workload quietly wanders out of the formula, presumably hoping nobody notices.

3. Warranty Hours/RO is hardcoded

The warranty car-count formula divides by 2, but that assumption is buried inside the formula. It should be a visible adjustable input:

Warranty Hours/RO Target: 2.0

The same should exist for internal hours per RO.

4. Working-day assumptions are inconsistent

Your technician-based potential uses 22 working days:

Tech count × 8 hours × 22 days × utilization

Your facility potential uses 24 working days:

Bays × 8 hours × 24 days

That can be valid only when the bays are open 24 days while technicians average 22 productive days, but it needs to be explicit. Otherwise, use separate clearly labeled assumptions:

Facility Operating Days
Average Technician Working Days

This would also make PTO, training, holidays, and four-day schedules easier to model correctly.

5. “Unapplied Time” becomes misleading above 100% proficiency

At 110% proficiency, the formula produces a positive $44,352 and adds it to service gross. That is not unapplied time. It is incremental productive contribution above clock-hour capacity.

I would split this into two concepts:

Unapplied Labor Cost, when proficiency is below 100%
Proficiency Gain, when proficiency is above 100%

Or better, eliminate the separate line and calculate labor gross directly from produced hours:

Produced FRH = Available Technician Hours × Utilization × Proficiency

Labor GP = Produced FRH × ELR × Labor Margin

That is cleaner and avoids turning “unapplied time” into a positive number, which is the spreadsheet equivalent of calling overtime “unused attendance.”

Naming changes

I would rename several lines for precision:

Current label	Recommended label
True Potential (FRH)	Staffed Production Capacity
Facility Potential (FRH)	Physical Facility Capacity
Facility GP Potential	Facility Gross Potential
% of Fac Pot	Target Capture of Absolute Capacity
% of Target	FGP vs. Current Target
Calendar Utilization	Technician Availability or Paid-Hour Availability
Proficiency	Productivity / Proficiency depending on exact definition

“Calendar utilization” is particularly ambiguous. In dealership reporting, utilization, proficiency, productivity, and efficiency are routinely mixed together until nobody knows whether the technician, bay, clock, or calendar is being measured.

The biggest strategic improvement

The sheet should show three states side by side:

Metric	Current State	Proposed Scenario	Incremental Impact
Technician count	42	46	+4
Produced FRH	6,801	X	+X
Service GP	$1.613M	X	+$X
Parts GP	$991K	X	+$X
Facility GP	$2.604M	X	+$X
Daily ROs needed	X	X	+X
Appointments needed	X	X	+X

That would make the calculator interview-ready. You could change technician count from 42 to 46 and immediately say:

Four additional productive technicians generate approximately X additional monthly FRH, X additional gross, and require X additional daily appointments to support them.

That is a management argument, a staffing case, and an operating plan in one view.

Bottom line

The underlying idea is very good. The calculator already demonstrates that MB Seattle’s $2 million target is not constrained by its facility. It is constrained by how effectively the store staffs, feeds, and manages the available capacity.

The appointment calculation and workload-mix logic need correction before you rely on it in a serious presentation. Once those are fixed and the model shows current versus scenario versus incremental gain, this becomes a credible Facility Gross Potential Scenario Model, not merely a worksheet.

mb seattle(1).xlsx
Spreadsheet
mb seattle(2).xlsx
Spreadsheet
Pasted text(2).txt
Document
Sun, Jul 19 at 7:44 AM
Pasted code.py
Python
Pasted code(1).py
Python
Pasted code.html
File
Pasted code(2).py
Python
give you full main.py  
screenshot of github
all good with exception we already have adr subfolder with ADR-001 through adr-006.  see screen shot..   
Pasted markdown.md
File
here is business-model-model.md   help me update properly  then we will do the same with object-relationships.md  
Pasted markdown(1).md
File
this is the object-relationship.md file  help me update it for update 3.. 
repo_files.txt
Document
Pasted text(3).txt
Document
Pasted text(5).txt
Document
Pasted text(6).txt
Document
mb seattle(3).xlsx
Spreadsheet
the 100% proficiency also supports our dependency flattening we are discussing in the book...   if you remember i built this spreadsheet to understand what was needed for the mb seattle opportunity.. 

Let's stress-test it against messy dealership reality rather than a cooperative textbook example. If Domain 6 survives these, I'd be comfortable freezing it.

Smoke Test 1: CSI is bad, but the shop is performing

Situation: CSI falls below benchmark. Management naturally wants to hold a CSI meeting, because meetings remain humanity's preferred treatment for numbers.

MI sees:

Appointment access healthy
Video execution healthy
Status communication healthy
Promise attainment healthy
First-Time Fix healthy
Comebacks normal
CSI below benchmark
Survey count: 9
Two highly negative surveys account for most of the decline
MI conclusion

Customer Outcome Variance: Low Confidence

CSI is below target, but current operational experience indicators do not show a corresponding systemic deterioration. Current survey volume is insufficient to establish a broad operating constraint.

Management Attention: None required at this time.

MI will continue monitoring survey volume, complaints, retention and operating indicators.

PASS.

This is important. MI must be capable of saying do nothing yet.

Otherwise we've simply invented a more sophisticated alarm system.

Smoke Test 2: CSI problem is actually a Promise problem

Situation: CSI deteriorates and complaints repeatedly mention delays and poor communication.

MI works upstream.

Customer Outcome

CSI ↓
Complaints ↑

Resolution

First-Time Fix healthy
Comebacks normal

Not primarily repair quality.

Promise

Promise attainment ↓
Promise misses concentrated in same-day repairs

Communication

Status communication is occurring, but mostly after promises have already failed.

Now we're getting somewhere.

Operations

Route Sheet shows:

Vehicles sitting Awaiting Dispatch
Several repairs started too late in the day
Technician capacity exists
Parts availability normal
Diagnosis

Primary Customer Experience Constraint: Promise Reliability

Customer dissatisfaction is concentrated around missed completion commitments. Available shop capacity is sufficient, but work is entering production too late to support established promises.

Likely upstream constraint: Dispatch / production-flow process.

Management Action

Correct dispatch timing for promise-sensitive ROs and use Promise at Risk intervention before customer commitments fail.

ASM Route Sheet sees individual threatened promises.

Service Manager sees concentration by ASM/disposition.

GM sees:

8 Promises At Risk | Primary Cause: Dispatch Flow

PASS.

Notice MI didn't tell anyone to "improve communication." Communication was a symptom downstream of production flow.

Smoke Test 3: Customer Access is poor, but hiring isn't the answer

This one really tests our cross-domain reasoning.

Situation:

Appointment lead time = 11 days
Customers complain about inability to get appointments
Retention begins declining
Shop has 14 technicians
Calendar utilization healthy
Technician Productivity only 68%
Technician Proficiency 82%
A/B technicians overloaded
C/D technicians underutilized
Maintenance/light repair demand is being routed heavily through B technicians

A primitive system concludes:

Need more technicians.

MI works upstream.

Customer Outcome

Retention ↓

↓

Access

Appointment lead time ↑
Demand healthy

↓

Capacity

Nominal technician headcount sufficient
Actual production below required FRH

↓

Technician system

Productivity ↓
Proficiency ↓
Capacity unevenly utilized

↓

Capability / Work Mix

A/B capacity overloaded
C/D capacity underutilized
Significant C/D-compatible work assigned upstream

MI conclusion

Primary Access Constraint: Work Mix / Capability Alignment

Customer demand exceeds currently realized production capacity, but the operation does not appear structurally understaffed. Available technician capacity is being constrained by work assignment and skill utilization.

Management Action: Rebalance identified maintenance/light-repair work toward capable C/D technicians before adding headcount.

That is exactly what we wanted when we built the A/B/C/D architecture.

STRONG PASS.

Smoke Test 4: Video is high, sales are weak, CSI is fine

This tests our Domain 6 / Domain 7 boundary.

Situation:

Video created: 94%
Video delivered: 91%
Video viewed: 76%
Customer satisfaction healthy
Status healthy
Controllable sales weak
Recommendations identified at healthy rate
Authorization weak
Domain 6 conclusion

Visual Service Communication is functioning reasonably well.

No significant Customer Experience constraint.

Domain 7 handoff

MI passes the evidence forward:

Opportunities are being discovered and customers are receiving/viewing visual evidence, but authorization is below expectation.

That's an Opportunity Conversion problem.

Domain 6 should not claim video failure merely because sales are weak.

PASS.

This validates our decision that video has two roles:

Domain 6: transparency/communication
Domain 7: presentation/conversion

Smoke Test 5: The ugly one

Customer comes in for a warning light.

Initial diagnosis requires an A technician.

Vehicle waits a day for diagnosis.

A technician diagnoses it correctly.

Part is backordered.

Customer receives regular Status communication and is told the ETA.

Part arrives four days later.

Advisor schedules customer promptly.

Repair completed correctly.

Total elapsed time: 8 days.

Customer survey: excellent.

A traditional cycle-time dashboard screams:

RO AGE: 8 DAYS 🔴

Domain 6 asks:

Access: acceptable
Communication: healthy
Promise Integrity: healthy
Resolution: First-Time Fix
Outcome: positive

Domain 4/5 understand:

External supply constraint, valid ETA, properly monitored.

MI conclusion

No controllable Customer Experience constraint identified.

That's a crucial pass.

Long cycle time does not automatically equal poor customer experience.

The customer knew what was happening, expectations were maintained, and the repair was completed correctly.

MI should not manufacture a management failure because an OEM couldn't supply a part.

One hole the smoke test exposes

I think we're missing one canonical concept:

Customer Effort

Not necessarily a formal score. I wouldn't create another survey requirement.

But MI needs to understand avoidable customer friction.

Examples:

Customer has to call four times for status.

Customer gets transferred repeatedly.

Customer arrives because vehicle was supposedly ready but it isn't.

Customer returns because paperwork wasn't complete.

Customer has to repeat the concern to multiple people.

Customer makes an unnecessary additional visit.

These may not immediately show up in CSI, comeback, promise attainment or retention.

The canonical concept could be:

Customer Effort / Friction: Avoidable additional actions required of the customer to complete the service experience.

MI could infer some of this from connected systems over time rather than requiring manual entry.

I would put Customer Effort under Promise & Convenience, because convenience isn't merely amenities. It's also:

How difficult did we make this transaction?

That makes Convenience much more meaningful.

Domain 6 after smoke test

I would make that one addition and then freeze:

1. Access
Demand → availability → scheduled load → arrival → production capacity.

2. Communication
Initial → visual service/video → decision → Status.

3. Promise & Convenience
Promise → revised expectation → ready → notification → delivery, plus Customer Effort/Friction.

4. Resolution & Quality
First-Time Fix → comeback → rework → repeat concern → recovery.

5. Customer Outcome
Satisfaction → complaints → retention → behavioral outcomes.

And MI-derived intelligence sits above it:

Promise at Risk
Promise Integrity
Commitment Risk
Constraint attribution
Materiality
Evidence confidence

Smoke-test verdict: PASS

With Customer Effort/Friction added, I would freeze Domain 6: Customer / Service Experience v1.

More importantly, the tests show the architecture doing what we intended:

It doesn't manage CSI. It manages the operating conditions that create the customer experience.

That's a significant distinction.

smoke test 1.. the 2 low surveys need to be reviewed despite what MI sees.  this might be a manager intervention to review surveys and input results to help MI.    other than that i agree however we are adding all of this MI intelligence.. how are we going to get that evidence for MI to determine actions

Your correction to Smoke Test 1 is right. Low sample size should reduce MI's confidence in a systemic diagnosis, but it should never cause MI to ignore an individual customer failure.

Those two bad surveys are exceptions requiring review.

The manager interaction might be:

2 Customer Experience Exceptions Require Review

MI does not currently detect a systemic operating pattern. Review these two negative surveys and classify the primary cause.

Then give the manager a very small structured input:

Access | Communication | Promise | Quality/Resolution | Price/Value | Employee Interaction | Other

Perhaps a secondary cause and a short optional note.

That human judgment becomes new evidence for MI. If both managers classify them as Promise failures, MI can go back into the operational data and look for supporting evidence. That's a legitimate reason to interrupt a manager because MI cannot know everything from transactional data.

And that gets directly to your bigger question.

Where does all this MI evidence actually come from?

This is probably the architecture discussion we need before adding much more intelligence.

We should not assume MI magically knows all this stuff. It needs an Evidence Architecture.

I see five evidence sources.

1. Direct system evidence

This should be our strongest source and require zero manager input.

From DMS and other integrations:

RO data

Open/close timestamps
Labor operations
FRH
labor types
parts
sales
technician assignments
advisor
VIN
promised time, if captured
status/disposition where available

Technician data

Clocked time
actual working time
FRH produced
technician assignment
training/certifications where available

Parts

Inventory
aging
sales
SOR
backorders
receipts
buyouts
stocking status

Appointments

created
scheduled
arrived
cancelled
no-show

This is the factual foundation.

2. Connected execution-system evidence

This is where MI becomes much stronger than DMS-only analytics.

Inspection/video systems can provide:

MPI completed → Red/Yellow findings → video created → video delivered → video viewed → recommendations → authorization

Communication systems can provide:

Text sent → customer response → phone contact → status communication → estimate delivered

Scheduling systems provide appointment behavior.

OEM systems provide CSI, retention, warranty and potentially training/certification information.

Accounting systems provide financial results.

MI doesn't necessarily need one giant integration on day one. The architecture needs to allow evidence adapters from different sources.

3. Derived evidence

This is where our canonical model starts doing work.

MI takes raw facts and calculates things humans currently spend time figuring out:

Productivity
Efficiency
Proficiency
DSO
Turns
GP/RO
ELR % of Door Rate
Parts-to-Labor
Appointment Lead Time
Promise Attainment
RO Aging
Technician Capacity
Required FRH
Work-mix distribution

This evidence doesn't require someone to enter it. MI derives it.

4. Inferred evidence

Now we enter actual intelligence.

Suppose MI sees:

Promise at 4:00
RO awaiting dispatch at 1:30
3.4 FRH remaining
appropriate technician capacity constrained

MI can infer:

Promise at Risk

That's not directly stored anywhere. MI derived a conclusion from several facts.

Or:

DSO high + Turns low + 10–12 growing + recurring buyouts for high-demand parts

MI infers:

Likely Inventory Mix Constraint

This is where I think we need an Evidence Confidence model.

Something like:

Observed = directly sourced fact
Calculated = deterministic calculation
Inferred: High Confidence = strong evidence relationship
Inferred: Moderate Confidence = probable relationship
Judgment Required = insufficient evidence for reliable diagnosis

Not necessarily those exact names in the UI, but the reasoning engine needs to know the difference.

5. Human judgment evidence

This is the part your survey correction exposes.

There are things MI simply cannot reliably know.

A customer writes:

"Nobody cared about me."

The DMS cannot explain that.

So MI asks a manager only because judgment is necessary.

Manager reviews the survey and classifies:

Primary cause: Employee Interaction
Secondary cause: Status Communication
Corrective action: Advisor coaching

Now that becomes evidence.

And importantly, MI remembers it.

If eight negative surveys over three months involving the same ASM are classified similarly, MI now has a pattern it couldn't have discovered from RO timestamps alone.

That is exactly the kind of manager participation worth asking for.

I think we need an Evidence Object

This feels architectural enough that we should eventually model it explicitly.

Every important MI conclusion should be traceable:

MI CONCLUSION
     │
     ├── Direct Evidence
     │
     ├── Calculated Evidence
     │
     ├── Inferred Evidence
     │
     └── Human Judgment
              ↓
       Confidence
              ↓
       Recommended Action

For example:

Likely Constraint: Dispatch Flow

Click Why?

MI shows:

Observed

11 promise misses this week
8 were awaiting dispatch within 2 hours of promise

Calculated

Available technician capacity was sufficient during 6 of those events

Inferred

Dispatch timing is the common upstream constraint
Confidence: High

Human evidence

Service Manager previously confirmed dispatch process inconsistency

Now the manager can challenge MI too:

Not correct

and classify why.

That correction becomes intelligence rather than disappearing into the ether.

This also answers how we build MI progressively

We don't need every integration on Day One.

Think of MI intelligence as becoming richer with available evidence.

Basic implementation

DMS + financial data.

MI can already understand quite a lot:

Financial → volume → RO economics → technician production → Parts → aging → customer outcomes

Intermediate

Add appointments + MPI/video + communication + CSI.

Now MI understands:

Access → discovery → communication → authorization → customer experience

Advanced

Add route-sheet events, technician actual working time, SOR/Parts events, OEM systems, deeper communications.

Now we get:

real-time Promise at Risk, lost productive time, constraint attribution, work-mix intelligence, predictive management intervention.

Same canonical architecture. Increasing evidence resolution.

That's important commercially too. MI doesn't become useless because Dealer Group X uses different systems than AutoNation.

And this reinforces our Manager Participation Principle

The hierarchy becomes:

Observe → Calculate → Infer → Corroborate → Ask only if unresolved/material → Learn → Monitor

I'd actually add Corroborate now.

Before bothering a manager, MI should search its other evidence sources for confirmation.

Only then:

Human judgment required.

And your survey example is perfect:

Two negative surveys detected
→ MI reviews operational evidence
→ no clear causal pattern
→ individual failures are material enough to understand
→ manager review required
→ classifications become evidence
→ MI learns from them.

So I would amend Smoke Test 1:

No evidence yet of a systemic Customer Experience constraint. However, two negative customer experiences require management review and classification.

That's much better than "no action required."

And I think before we freeze Domain 6, we should memorialize this Evidence Architecture, because without it we've designed a very intelligent brain without adequately specifying where its senses come from.

ok.. i agree.. lets memorialize and Freeze

Memorialized and frozen.

Session 018 captures both major decisions from tonight:

Domain 6: Customer / Service Experience v1 — FROZEN
MI Evidence Architecture v1 — FROZEN

It also incorporates your Smoke Test 1 correction: low survey volume may reduce confidence in a systemic problem, but individual negative surveys still require management review, with that judgment feeding MI's evidence base.

Download Session_018.md

Next restart point is Domain 7: Sales / Opportunity Conversion. That's going to be an important one because we'll finally generalize all the controllable-sales work into automotive-canonical architecture without accidentally building AutoNation into the foundation. 

Session_018.md
Document

Library
/
Session_018.md
MI v5 --- Session 018
Domain 6: Customer / Service Experience & MI Evidence Architecture

Date: August 14, 2026
Project: ProdTracker Management Decision Platform --- Management
Intelligence v5
Status: Architecture / Domain Definition
Session Outcome: Domain 6 --- Customer / Service Experience v1
FROZEN; MI Evidence Architecture v1 FROZEN

1. Session Purpose

Define the canonical Customer / Service Experience domain while ensuring
MI can obtain enough evidence to diagnose causes without creating
manager workload.

The session also formalized how MI obtains, evaluates, combines, and
learns from evidence.

2. Domain 6 Definition --- FROZEN

Customer / Service Experience measures the customer's ability to
access service, understand what is happening, make informed decisions,
receive the vehicle in accordance with maintained expectations, have
the concern resolved correctly, and continue the relationship with the
dealership.

CSI and other survey measurements are outcomes, not diagnoses.

Frozen causal structure:

Access → Communication → Promise & Convenience → Resolution &
Quality → Customer Outcome

MI diagnoses backward from downstream outcomes toward the earliest
material controllable upstream constraint.

ACCESS
3. Access --- FROZEN v1

Manager questions:

Do we have enough customer demand?
Can customers get in when they need to?
Are we matching demand to actual shop capacity?

Canonical reasoning chain:

Demand → Appointment Availability → Scheduled Load → Arrival →
Production Capacity

Supporting concepts may include appointment requests, appointment
volume, walk-ins, days to next available appointment, Appointment Lead
Time, available appointment capacity, utilization, conversion, shows,
no-shows, cancellations, and reschedules.

Appointment volume is not the objective. Scheduled demand must be
matched to real production capacity.

MI should distinguish Demand, Access, Scheduling, Capacity, and
Show-Rate constraints.

Access connects upstream to Domain 4 Technician & Capacity, including
technician capability and work mix.

COMMUNICATION
4. Communication --- FROZEN v1

Manager question:

Does the customer understand what is happening, what is recommended,
what happens next, and where the vehicle currently stands?

Canonical structure:

Initial Communication → Visual Service Communication → Decision
Communication → Status Communication

Initial Communication

Establish the concern, expected timing, communication method, and
initial expectation.

Visual Service Communication

Video belongs in Domain 6 as a transparency and communication mechanism.

Potential measures where supported: - Video Creation Rate - Video
Delivery Rate - Video View Rate - Video Timeliness

Video crosses into Domain 7 as presentation/conversion evidence.

Domain 6 asks whether the vehicle condition was communicated clearly and
transparently. Domain 7 asks whether the identified opportunity
converted.

Decision Communication

Need Discovered → Customer Informed → Recommendation Presented →
Customer Decision

Potential evidence includes discovery-to-presentation time,
presentation-to-decision time, unanswered recommendations, and
authorization/decline status.

Status Communication

Status is the canonical dealership communication term.

Status Communication = keeping the customer informed of
vehicle/repair status and communicating material changes to the
established expectation.

MI should emphasize exception communication rather than arbitrary
repetitive contact requirements.

Expectation Established → Material Condition Changes → Customer
Informed → Revised Expectation Established

PROMISE & CONVENIENCE
5. Promise & Convenience --- FROZEN v1

Manager question:

Did we make it reasonably easy to do business with us, and did we do
what we told the customer we would do?

Canonical concepts: - Promised Completion Time - Vehicle Ready Time -
Customer Notified Ready Time where available - Vehicle Delivery / RO
Close Time - Promise Attainment - Promise Miss Duration - Revised
Promise / Expectation - Mobility / Service Convenience where
applicable - Customer Effort / Friction

Promise Integrity

When circumstances change, MI asks whether the dealership communicated
the change and established a realistic revised expectation before the
prior commitment failed.

Customer Effort / Friction

Avoidable additional actions required of the customer to complete
the service experience.

Examples may include repeated status calls, unnecessary return visits,
repeated explanation of the concern, or arriving for a vehicle that is
not actually ready.

This should be inferred where possible rather than manually tracked.

6. Promise at Risk --- FROZEN Architecture

Promise at Risk is an RO-level MI intelligence object.

ASM Route Sheet

The ASM sees the individual RO while action is still possible: - Promise
time - Current disposition - Remaining expected work - Time remaining -
Likely constraint - Required action

ASM objective:

Protect the promise → resolve the constraint → or revise the
customer expectation before the commitment fails.

Service Manager / FOD

Aggregated view of at-risk promises, concentrations, constraints, ASMs,
and required intervention.

GM / Main Page

Executive aggregation of promises at risk, high-risk promises, primary
constraints, and potential customer/financial exposure.

Decision Journal

Escalate only when material enough to require a management decision or
commitment.

Potential risk states: Watch, At Risk, Critical, Missed. Retain only
states that change behavior.

RESOLUTION & QUALITY
7. Resolution & Quality --- FROZEN v1

Manager question:

Did we fix the vehicle correctly the first time?

First-Time Fix / Fixed Right First Time

Desired outcome: the concern or repair is correctly resolved during the
initial repair event without subsequent corrective work for the same
issue.

Comeback

A vehicle returns because prior work did not correctly resolve the
concern or created a related problem. A return visit alone is not
automatically a comeback.

Rework

Previously performed work requires correction before successful
completion/delivery.

Repeat Repair / Repeat Concern

A relationship signal requiring classification. Repeat does not
automatically equal comeback.

Goodwill / Service Recovery

Evidence of recovery activity, not proof of a comeback or quality
failure.

MI should evaluate quality failures through People, Platform, Process,
and Performance, including technician capability and work-mix alignment.

CUSTOMER OUTCOME
8. Customer Outcome --- FROZEN v1

Manager question:

Did the customer's experience produce satisfaction, trust, and
continued relationship with the dealership?

Customer Satisfaction Measurement

Canonical concept covering tenant/OEM implementations such as CSI, OEM
surveys, dealer-group surveys, NPS, and tenant-specific measures.

MI should preserve source methodology, benchmark/target, response count,
response rate, measurement period, and source where available.

MI should not combine incompatible survey systems into a meaningless
universal score.

Service Retention

Primary behavioral outcome. Eligibility and calculation methodology
remain tenant/OEM configurable.

Other potential signals include repeat service behavior, customer
defection, and return interval.

Relationship / Recovery

Potential concepts: - Customer Complaint - Service Recovery Event -
Escalation - Resolution Status

These remain source-dependent.

DOMAIN 6 SMOKE TEST
9. Smoke Test 1 --- Low Survey Volume --- CORRECTED

Scenario: - CSI below benchmark - 9 surveys - 2 highly negative
surveys - Operational indicators otherwise healthy

Frozen correction

Low sample size reduces confidence in a systemic diagnosis, but it
does not justify ignoring individual customer failures.

The two negative surveys require management review.

Desired MI behavior:

2 Customer Experience Exceptions Require Review

MI does not currently detect a systemic operating pattern. Review the
two negative surveys and classify the primary cause.

Potential manager classification: - Access - Communication - Promise -
Quality / Resolution - Price / Value - Employee Interaction - Other

Optional secondary cause and short note may be captured.

The manager's classification becomes MI evidence.

Low confidence in a systemic problem does not eliminate the need to
review material individual customer failures.

10. Other Smoke Tests --- PASS

Promise failure: CSI/complaints traced through poor promise
attainment to Dispatch/Production Flow.

Poor access without staffing shortage: appointment lead time and
retention traced to Work Mix / Capability Alignment rather than
automatic headcount addition.

Video high, sales weak: Domain 6 recognizes healthy visual
communication and hands conversion analysis to Domain 7.

Long cycle time with OEM backorder and good communication: no
controllable Customer Experience constraint when expectations are
maintained and repair is correct.

MI EVIDENCE ARCHITECTURE
11. Evidence Architecture --- FROZEN v1

Every material MI conclusion must be supported by evidence, gathered
with the least possible manager participation.

Evidence Source 1 --- Direct System Evidence

Examples: - RO timestamps, operations, FRH, labor type, parts, sales,
technician, advisor, VIN, promise, disposition - Technician clocked
time, actual working time, FRH, assignments, certifications where
available - Parts inventory, aging, sales, SORs, backorders, receipts,
buyouts, stocking status - Appointment creation, schedule, arrival,
cancellation, no-show

Evidence Source 2 --- Connected Execution Systems

Examples: - MPI completion and findings - Video
created/delivered/viewed - Recommendations and authorization -
Text/customer response - Phone/status events - Estimate delivery - OEM
CSI/retention/warranty/training systems - Accounting systems

Architecture should support different tenant evidence adapters rather
than one universal vendor stack.

Evidence Source 3 --- Derived Evidence

Examples: - Productivity - Efficiency - Proficiency - DSO - Turns -
GP/RO - ELR % of Door Rate - Parts-to-Labor - Appointment Lead Time -
Promise Attainment - RO Aging - Technician Capacity - Required FRH -
Work-mix distribution

Evidence Source 4 --- Inferred Evidence

MI combines facts and calculations to infer conditions such as: -
Promise at Risk - Inventory Mix Constraint - Dispatch/flow constraint -
Work-mix/capability constraint

Evidence Source 5 --- Human Judgment

Used when transactional evidence cannot reliably resolve material
context, such as: - Why a customer felt ignored - Whether a repeat
repair is truly related - Context behind a survey complaint - Whether
MI's inferred cause is wrong - Management choice among reasonable
remedies

Human judgment becomes persistent evidence.

12. Evidence Confidence --- FROZEN Concept

MI must understand the origin and strength of evidence.

Conceptual classes:

Observed --- directly sourced fact
Calculated --- deterministic result from observed facts
Inferred: High Confidence --- strong evidence relationship
Inferred: Moderate Confidence --- probable relationship with
meaningful uncertainty
Judgment Required --- insufficient evidence for reliable
diagnosis

Exact UI terminology can evolve later.

13. Corroboration Rule --- FROZEN

Before interrupting a manager, MI should seek corroboration through
other available evidence.

Observe → Calculate → Infer → Corroborate → Ask only if
unresolved/material → Learn → Monitor

14. Evidence Object --- Architecture Concept

Every important MI conclusion should eventually be traceable:

MI Conclusion
      │
      ├── Observed Evidence
      ├── Calculated Evidence
      ├── Inferred Evidence
      └── Human Judgment
                ↓
           Confidence
                ↓
       Recommended Action

Managers should have a clear Why? path without having to perform the
diagnosis themselves.

15. Manager Correction Becomes Intelligence

Managers must be able to challenge MI conclusions.

A correction such as Not Correct should allow the manager to provide
missing context or classification.

That correction becomes evidence and improves future reasoning rather
than disappearing after the interaction.

This supports the future Management Decision Journal and institutional
management memory.

16. Progressive Evidence Resolution

MI does not require every integration on Day One.

Basic

DMS + financial data.

Intermediate

Add appointments, MPI/video, communication, and CSI.

Advanced

Add route-sheet events, actual technician working time, detailed
SOR/Parts events, OEM systems, and deeper communications.

The canonical architecture remains stable while evidence resolution and
MI confidence increase.

MANAGER PARTICIPATION
17. Manager Participation Principle --- FROZEN

MI should require management participation only when human judgment,
authority, or action is necessary. Observation, calculation,
diagnosis, monitoring, and routine follow-up should be automated
wherever reliable data permits.

Short product rule:

Don't ask the manager to tell MI what MI can already know.

Participation hierarchy:

Observe automatically
Derive automatically
Diagnose automatically
Recommend automatically
Ask the manager only when judgment is required
Remember the manager's decision
Monitor automatically
Re-engage on exception
FINAL DOMAIN 6 ARCHITECTURE
18. Frozen Structure
1. Access

Demand → Availability → Scheduled Load → Arrival → Production
Capacity

2. Communication

Initial Communication → Visual Service Communication → Decision
Communication → Status Communication

3. Promise & Convenience

Promise → Material Change → Revised Expectation → Ready →
Notification → Delivery

Includes Promise Attainment, Promise Integrity, Promise at Risk,
Customer Effort/Friction, and mobility/convenience where applicable.

4. Resolution & Quality

First-Time Fix, Comeback, Rework, Repeat Repair/Concern,
Goodwill/Service Recovery.

5. Customer Outcome

Customer Satisfaction Measurement, tenant/OEM CSI mappings, Retention,
behavioral outcomes, complaints, recovery, and escalation.

19. Diagnostic Direction

Operational experience flows:

Access
  ↓
Communication
  ↓
Promise / Convenience
  ↓
Resolution / Quality
  ↓
Customer Outcome

MI diagnoses upstream:

CSI / Retention / Complaint
          ↓
Resolution?
          ↓
Promise?
          ↓
Communication?
          ↓
Access?
          ↓
Parts / Capacity / Work Mix / Process / People
          ↓
EARLIEST MATERIAL CONTROLLABLE CONSTRAINT
20. Session Decisions --- FROZEN
Domain 6 Customer / Service Experience v1
Access architecture and Appointment Lead Time
Demand versus production-capacity reasoning
Communication architecture
Status as canonical dealership communication concept
Visual Service Communication/video in Domain 6
Video handoff into Domain 7
Promise Attainment and Promise Integrity
Customer Effort/Friction
Promise at Risk as an RO-level intelligence object
Promise at Risk on ASM Route Sheet and manager/GM pages
First-Time Fix, Comeback, Rework, Repeat Repair/Concern
Goodwill/Service Recovery distinction
Customer Satisfaction Measurement as canonical concept
Tenant/OEM-specific CSI mappings
Retention as behavioral outcome
Negative surveys require review even when systemic confidence is low
Human survey classification becomes MI evidence
MI Evidence Architecture v1
Direct, connected-system, derived, inferred, and human-judgment
evidence
Evidence Confidence
Corroboration before manager interruption
Evidence Object architecture concept
Manager corrections become persistent intelligence
Progressive evidence resolution
Manager Participation Principle
21. Next Starting Point
Domain 7 --- Sales / Opportunity Conversion

Key challenge:

Separate universal automotive opportunity concepts from
AutoNation-specific controllable-sales metrics.

Likely areas: - Opportunity discovery - MPI findings - Recommendations -
Presentation - Video as conversion evidence - Authorization - Declines -
Deferred work - Maintenance - Tires - Brakes - Batteries - Alignments -
Other repair categories - Conversion/capture - Work-mix consequences -
GP opportunity - ODI / OCI and proprietary MI intelligence

Session Closing Principles

Customer feedback tells us what the customer experienced.
Operational intelligence should tell management what caused it and
what to do about it.

Low confidence in a systemic problem does not eliminate the need to
review material individual customer failures.

Observe → Calculate → Infer → Corroborate → Ask only if
unresolved/material → Learn → Monitor.

Don't ask the manager to tell MI what MI can already know.

The depth belongs inside MI, not in the manager's workload.

Complexity belongs in the system. Management receives the fewest
actionable items necessary to materially improve the operation.