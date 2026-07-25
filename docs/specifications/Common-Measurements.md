# Common Measurements Specification

## Purpose

Every Intelligence Domain must calculate measurements exactly the same way.

There should never be multiple definitions for:

- Gross Profit
- Hours per RO
- ELR
- Efficiency
- CSI
- Opportunity %
- Pace to Budget

A measurement exists only once.

Everything else references it.

---

# Measurement Standard

Every measurement includes:

- Name
- Business Definition
- Calculation
- Inputs
- Frequency
- Aggregation
- Display Format
- Owner
- Dependencies

---

# Example

## CP Gross Profit per RO

### Business Definition

Average Customer Pay Gross Profit earned for every completed Customer Pay Repair Order.

### Formula

```
CP Gross Profit
-----------------------
Completed CP Repair Orders
```

### Inputs

- Repair Orders
- Accounting
- Gross Profit
- Closed Status

### Frequency

- Daily
- Weekly
- Monthly
- Rolling

### Aggregation

- Store
- Market
- Region
- Enterprise

---

# Measurement Categories

## Financial

- Total Gross Profit
- Customer Pay Gross Profit
- Warranty Gross Profit
- Internal Gross Profit
- Wholesale Gross Profit
- Parts Gross Profit
- Labor Gross Profit
- Expense
- Service Absorption

---

## Productivity

- Hours per RO
- Flat Rate Hours
- Technician Efficiency
- Effective Labor Rate
- Gross Profit per Hour
- Hours Sold
- Hours Produced

---

## Sales

- Video Creation %
- Video View %
- Declined Service %
- Red Opportunity %
- Yellow Opportunity %
- Conversion %
- Menu Presentation %
- Tire Sales %
- Brake Sales %
- Battery Sales %
- Alignment Sales %

---

## Customer

- CSI
- Net Promoter Score
- Appointment Show %
- No Show %
- Waiter %
- Task Completion %
- Response Time

---

# Measurement Hierarchy

```
Raw Data

↓

Measurements

↓

Signals

↓

Insights

↓

Recommendations

↓

Management Decisions
```

---

# Guiding Principle

> Measurements describe reality.

> Intelligence explains reality.

> Management changes reality.