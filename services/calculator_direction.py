"""Explain what to check before using a calculator to change the shop’s plan."""

CHECKS = {
    "sci_coverage": {
        "label": "Structural Concentration Indicator (SCI)",
        "limit": "Check where critical work relies on one person and identify a backup.",
        "trial": "Have a second person run the job or responsibility through a handoff.",
        "verify": "Record who covered the work, what evidence confirms it, and which gaps remain.",
    },
    "tsi_development": {
        "label": "Technician Sustainability Index (TSI)",
        "limit": "Check which critical jobs need more technicians who can do the work independently.",
        "trial": "Give a learner supervised work and set a date to verify independent completion.",
        "verify": "Record the RO or sign-off and check whether independent coverage improved.",
    },
    "uvi_coverage": {
        "label": "Utilization Variance Index (UVI)",
        "limit": "Review the work concentrated with one technician and verify which jobs need a qualified backup.",
        "trial": "Confirm a qualified backup and available time for the highest-priority work.",
        "verify": "Check which repair orders were covered, which hours were still exposed, and whether promises were kept.",
    },
    "mpi_calculator": {
        "label": "Added Lines",
        "limit": "Follow inspection findings through customer authorization before counting on more sold hours.",
        "trial": "Test the added hours on documented recommendations customers authorize.",
        "verify": "Compare authorized added lines and completed sold hours per customer-pay RO.",
    },
    "appt_calculator": {
        "label": "RO & Appointment",
        "limit": "Confirm who is working, what jobs are booked, and how often customers show before opening more slots.",
        "trial": "Set the booking plan around the work the shop can finish by the promise time.",
        "verify": "Compare appointments booked, arrivals, completed ROs, and promises kept.",
    },
    "cpgp_calculator": {
        "label": "CP Gross Profit Opportunity",
        "limit": "Pull customer-pay volume, sold hours, rates, and margins for the same period before using a gross target.",
        "trial": "Test one CP driver at a time using the same repair-order population and cost basis.",
        "verify": "Compare the next CP gross report with the expected change and check what caused the difference.",
    },
    "capacity_calculator": {
        "label": "Capacity Opportunity",
        "limit": "Check tech coverage, authorized work, and job mix before treating additional capacity as an opportunity.",
        "trial": "Test one change to coverage or work flow where there is enough demand to use the added hours.",
        "verify": "Check sold hours, promise times, and whether the change still works when a key tech is out.",
    },
    "pace_recovery_calculator": {
        "label": "Pace Recovery",
        "limit": "Reconcile booked hours, the DPO target, and remaining workdays before setting a recovery pace.",
        "trial": "Pick a recovery step the team can finish with the time and authorized work available.",
        "verify": "Check booked hours and promises kept against the recovery plan at the next checkpoint.",
    },
    "appointment_lift_calculator": {
        "label": "Appointment Lift",
        "limit": "Check show rate, authorized work, and the shop’s ability to finish it before adding appointments.",
        "trial": "Try a small booking change in the shifts that can absorb the added work.",
        "verify": "Check whether added appointments became arrivals, completed ROs, and sold hours without missed promises.",
    },
}


def calculator_direction(endpoint, case, result):
    checks = CHECKS[endpoint]
    potential = result["true_potential"]
    can_test = (
        potential["validation_status"] == "sufficient"
        and result["diagnosis"]["correction_allowed"]
        and potential["frh_gap"] > 0
    )
    holding_plan = potential["validation_status"] == "sufficient" and potential["frh_gap"] <= 0
    return dict(
        status="Test a change" if can_test else "Hold the plan" if holding_plan else "Check before changing the plan",
        direction=checks["trial"] if can_test else (
            "Booked hours meet the supported potential for this window. Keep watching the same measure."
            if holding_plan else checks["limit"]
        ),
        calculator=endpoint,
        verify=checks["verify"],
        actual_frh=potential["actual_frh"],
        scheduled=bool(case.scheduled_operating_dates),
        demand_frh=potential["supported_demand_frh"],
        process_known="process" not in result["evidence_profile"]["missing_domains"],
        period_start=case.period_start,
        period_end=case.period_end,
    )
