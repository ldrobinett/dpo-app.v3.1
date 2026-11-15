"""Model recovery above the current run rate with explicit shop and demand limits."""


def recovery_estimate(values):
    elapsed, remaining = values["elapsed_workdays"], values["remaining_workdays"]
    month_days = elapsed + remaining
    mtd, goal = values["mtd_actual_frh"], values["monthly_frh_goal"]
    run_rate = mtd / elapsed
    projected = mtd + run_rate * remaining
    gap = max(0, goal - projected)
    capacity, demand = values["extra_capacity_per_day"], values["extra_demand_per_day"]
    recoverable = 0.0 if not remaining or not gap else None
    if recoverable is None and capacity is not None and demand is not None:
        recoverable = min(gap, remaining * min(capacity, demand))
    mtd_gross, forecast_gross = values["mtd_actual_gross"], values["monthly_forecast_gross"]
    projected_gross = mtd_gross / elapsed * month_days if mtd_gross is not None else None
    gross_gap = max(0, forecast_gross - projected_gross) if forecast_gross is not None and projected_gross is not None else None
    avg_hours, avg_gross = values["avg_hours_per_ro"], values["avg_gross_per_ro"]
    return dict(
        mtd_expected=goal * elapsed / month_days,
        run_rate=run_rate, projected=projected, gap=gap,
        required_extra_per_day=gap / remaining if remaining else None,
        required_total_per_day=max(0, goal - mtd) / remaining if remaining else None,
        recoverable=recoverable, uncovered=gap - recoverable if recoverable is not None else None,
        extra_ros_per_day=recoverable / remaining / avg_hours
        if recoverable is not None and remaining and avg_hours else None,
        projected_gross=projected_gross, gross_gap=gross_gap,
        added_gross=recoverable * (avg_gross / avg_hours)
        if recoverable is not None and avg_hours and avg_gross is not None else None,
    )


def recovery_next_step(values, result):
    remaining = values["remaining_workdays"]
    capacity, demand = values["extra_capacity_per_day"], values["extra_demand_per_day"]
    if not remaining:
        return dict(action="Reconcile the month-end close and check what drove the final result.",
                    expected="Confirm the final booked hours and the gap to the monthly target.")
    if not result["gap"]:
        return dict(action="Protect the current booking pace and check it at the next huddle.",
                    expected="Confirm booked hours are still on track for the month and promises are being kept.")
    if capacity is None or demand is None:
        return dict(action="Confirm the spare shop time and authorized work for the remaining days.",
                    expected="Document additional FRH per day the shop can take on and the work available to fill it.")
    if result["recoverable"] <= 0:
        return dict(action="Find the limit: check dispatch, staffing, or authorized work before asking for more hours.",
                    expected="Identify what is holding recovery back and what the shop can change safely.")
    return dict(
        action="Confirm the spare shop time and authorized work, then assign and dispatch the recovery work.",
        expected=f"Book {result['recoverable']:,.1f} extra FRH over the remaining {remaining:g} workdays "
        f"above the {result['run_rate']:,.1f} FRH/day baseline, while keeping customer promises.",
    )
