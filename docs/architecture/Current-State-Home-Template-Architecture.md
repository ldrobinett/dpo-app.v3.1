Current-State Home Template Architecture

1. Purpose

2. Design Origin
   • Evolution from the original Excel workbook
   • Evolution through store contacts
   • Executive Operating Review workflow
   • Transition to Management Intelligence

3. Architectural Philosophy
   • Decision support before reporting
   • Manager workflow over software workflow
   • Operational questions drive layout

4. Template Hierarchy
   • base.html
   • home.html
   • inheritance
   • blocks

5. Data Contract
   • main.home()
   • render_template()
   • variables passed

6. Dashboard Workflow
   Executive Summary
       ↓
   Today's Focus
       ↓
   Daily Targets
       ↓
   Appointment Capacity
       ↓
   Work Opportunity
       ↓
   Route Sheet Action Board
       ↓
   Technician Performance
       ↓
   Hours Pace
       ↓
   Daily Metrics

7. Dashboard Card Analysis

   7.1 Executive Summary

   7.2 Today's Focus

   7.3 Daily Targets

   7.4 Appointment Information

   7.5 Work Opportunity

   7.6 Route Sheet Action Board

   7.7 Technician Performance

   7.8 Hours Pace

   7.9 Daily Inputs

8. Presentation Logic

9. Conditional Rendering

10. Collections

11. JavaScript

12. Architectural Strengths

13. Technical Debt

14. Future MI Opportunities

15. Current-State Conclusions

**NOTE**
The current Home Dashboard establishes the intended Management Intelligence user experience. However, its underlying recommendation logic remains primarily DPO-, pace-, WIP-, and rules-based. UVI, TSI, full scorecard execution intelligence, and outcome-based recommendation learning have not yet been implemented.