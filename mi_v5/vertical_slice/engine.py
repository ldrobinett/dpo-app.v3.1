"""Deterministic reasoning for Vertical Slice 1."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .contracts import (
    AttentionClass,
    CausalDiagnosis,
    ConditionState,
    ConditionType,
    DiagnosticConfidence,
    EvidenceDepthProfile,
    EvidenceQuality,
    ManagementPosition,
    MaterialCondition,
    StorePeriodEvidence,
    TruePotentialResult,
    VerticalSliceResult,
)


@dataclass(frozen=True)
class SlicePolicy:
    """Versioned implementation thresholds, not new architecture."""

    version: str = "vertical-slice-policy-v1"
    stale_after_days: int = 1
    intervene_gap_days: int = 2
    escalate_gap_ratio: float = 0.20
    material_realization_rate: float = 0.90


def _gp_per_frh(evidence: StorePeriodEvidence) -> float | None:
    values = evidence.economics
    required = (
        values.effective_labor_rate,
        values.parts_to_labor_ratio,
        values.labor_margin,
        values.parts_margin,
    )
    if any(value is None for value in required):
        return None
    assert values.effective_labor_rate is not None
    assert values.parts_to_labor_ratio is not None
    assert values.labor_margin is not None
    assert values.parts_margin is not None
    labor_gp = values.effective_labor_rate * (values.labor_margin / 100.0)
    parts_gp = (
        values.effective_labor_rate
        * values.parts_to_labor_ratio
        * (values.parts_margin / 100.0)
    )
    return labor_gp + parts_gp


def _capacity(
    evidence: StorePeriodEvidence,
) -> tuple[float, dict[date, float]]:
    by_date: dict[date, float] = {}
    total = 0.0
    for technician in evidence.technicians:
        for scheduled_date in technician.scheduled_dates:
            total += technician.dpo
            by_date[scheduled_date] = (
                by_date.get(scheduled_date, 0.0) + technician.dpo
            )
    return total, by_date


def evaluate_case(
    evidence: StorePeriodEvidence,
    policy: SlicePolicy | None = None,
) -> VerticalSliceResult:
    """Evaluate one period without converting absence into performance failure."""

    policy = policy or SlicePolicy()
    capacity_frh, capacity_by_date = _capacity(evidence)
    scheduled = set(evidence.scheduled_operating_dates)
    observed = set(evidence.production_dates)
    continuity_gaps = tuple(sorted(scheduled - observed))
    latest_observed = max(evidence.production_dates, default=None)
    freshness_days = (
        (evidence.period_end - latest_observed).days if latest_observed else None
    )

    missing_dpo_governance = any(
        technician.dpo_mode != "calculated" or technician.dpo <= 0
        for technician in evidence.technicians
    )
    missing_economics = _gp_per_frh(evidence) is None
    missing_demand = evidence.supported_demand_frh is None
    evidence_limited = bool(
        continuity_gaps or missing_dpo_governance or missing_demand
    )

    profile = EvidenceDepthProfile(
        breadth=("people", "operating_structure", "performance"),
        missing_domains=("process",),
        granularity=("daily", "repair_order", "employee"),
        historical_depth_days=(
            evidence.period_end - evidence.period_start
        ).days
        + 1,
        frequency="daily",
        freshness_days=freshness_days,
        completeness=(
            EvidenceQuality.LIMITED
            if evidence_limited
            else EvidenceQuality.SUFFICIENT
        ),
        continuity_gap_dates=continuity_gaps,
        reliability=(
            EvidenceQuality.LIMITED
            if evidence_limited
            else EvidenceQuality.SUFFICIENT
        ),
        scope=(
            "enterprise",
            "managed_store",
            "service_department",
            "technician",
        ),
        known=(
            "Technician DPO values and scheduled work dates are present.",
            "Produced FRH and repair-order identifiers are present for observed dates.",
            "Service economic inputs are present."
            if not missing_economics
            else "Service economic inputs are incomplete.",
        ),
        inferred=(
            "A scheduled date without a production record is an evidence-continuity gap, not proof of zero production.",
        ),
        unknown=tuple(
            item
            for item, missing in (
                (
                    "Supported demand is not represented by a governed source.",
                    missing_demand,
                ),
                (
                    "Legacy DPO authority and effective-period lineage are incomplete.",
                    missing_dpo_governance,
                ),
                ("Detailed Process evidence is unavailable.", True),
            )
            if missing
        ),
    )

    true_potential_frh = (
        min(capacity_frh, evidence.supported_demand_frh)
        if evidence.supported_demand_frh is not None
        else capacity_frh
    )
    gp_per_frh = _gp_per_frh(evidence)
    frh_gap = max(true_potential_frh - evidence.actual_frh, 0.0)
    realization = (
        evidence.actual_frh / true_potential_frh
        if true_potential_frh > 0
        else None
    )
    tp_limitations = tuple(
        limitation
        for limitation, present in (
            (
                "Supported demand is unavailable; the result is capacity potential, not validated True Potential.",
                missing_demand,
            ),
            (
                "Technician DPO records lack complete frozen-period governance lineage.",
                missing_dpo_governance,
            ),
            (
                "Production evidence is discontinuous across scheduled operating dates.",
                bool(continuity_gaps),
            ),
            ("Economic inputs are incomplete.", missing_economics),
        )
        if present
    )
    potential = TruePotentialResult(
        method_version="service-capacity-potential-v1",
        capacity_frh=round(capacity_frh, 2),
        supported_demand_frh=evidence.supported_demand_frh,
        true_potential_frh=round(true_potential_frh, 2),
        validation_status=(
            EvidenceQuality.LIMITED
            if tp_limitations
            else EvidenceQuality.SUFFICIENT
        ),
        gp_per_frh=(round(gp_per_frh, 2) if gp_per_frh is not None else None),
        true_potential_cp_gp=(
            round(true_potential_frh * gp_per_frh, 2)
            if gp_per_frh is not None
            else None
        ),
        actual_frh=round(evidence.actual_frh, 2),
        realization_rate=(
            round(realization, 4) if realization is not None else None
        ),
        frh_gap=round(frh_gap, 2),
        estimated_cp_gp_gap=(
            round(frh_gap * gp_per_frh, 2)
            if gp_per_frh is not None
            else None
        ),
        limitations=tp_limitations,
    )

    if continuity_gaps:
        gap_ratio = len(continuity_gaps) / max(len(scheduled), 1)
        unverified_capacity = sum(
            capacity_by_date.get(day, 0.0) for day in continuity_gaps
        )
        exposure = (
            unverified_capacity * gp_per_frh
            if gp_per_frh is not None
            else None
        )
        state = (
            ConditionState.ESCALATE
            if gap_ratio >= policy.escalate_gap_ratio
            else ConditionState.INTERVENE
            if len(continuity_gaps) >= policy.intervene_gap_days
            else ConditionState.MANAGE
        )
        condition = MaterialCondition(
            condition_type=ConditionType.CONSTRAINT,
            state=state,
            title="Production evidence continuity is incomplete",
            evidence=(
                f"{len(continuity_gaps)} scheduled operating date(s) have no production records.",
                f"Latest production evidence is {freshness_days} day(s) before period end.",
            ),
            materiality=tuple(
                item
                for item in (
                    f"{unverified_capacity:,.1f} FRH of scheduled DPO capacity falls inside the uncovered dates.",
                    (
                        f"${exposure:,.0f} of capacity-based CP gross is unverified, not established as lost."
                        if exposure is not None
                        else None
                    ),
                )
                if item is not None
            ),
            consequence=(
                "Actual-versus-potential performance cannot be judged reliably "
                "until the missing dates are reconciled."
            ),
        )
        diagnosis = CausalDiagnosis(
            hypothesis=(
                "Production evidence ingestion or source continuity failed for "
                "scheduled operating dates."
            ),
            confidence=DiagnosticConfidence.PROBABLE,
            supporting_evidence=(
                "Schedule evidence continues after the final observed production date.",
                (
                    "The missing records are contiguous at the end of the evaluated period."
                    if latest_observed
                    and all(day > latest_observed for day in continuity_gaps)
                    else "Missing production dates occur within the evaluated period."
                ),
            ),
            weakened_explanations=(
                "The observed FRH gap cannot be treated as verified technician underperformance.",
                "The observed FRH gap cannot support a Process diagnosis.",
            ),
            unresolved_explanations=(
                "The source may have failed to ingest completed work.",
                "The store may have produced zero FRH, but explicit zero-production evidence is absent.",
            ),
            correction_allowed=False,
        )
        attention = (
            AttentionClass.CRITICAL
            if state in {ConditionState.ESCALATE, ConditionState.CRITICAL}
            else AttentionClass.NEED
        )
        management_position = ManagementPosition(
            attention=attention,
            what_matters=(
                "Production evidence does not cover every scheduled operating date."
            ),
            why_it_matters=(
                "Acting on the apparent performance gap could assign accountability "
                "or prescribe recovery work from incomplete evidence."
            ),
            position=(
                "Verify evidence integrity before interpreting the "
                "Actual-versus-Potential gap."
            ),
            recommended_intervention=(
                "Reconcile the uncovered scheduled dates against the source system, "
                "restore missing production records or record governed zero-production "
                "evidence, then rerun this case."
            ),
            owner_id=evidence.accountable_owner_id,
            owner_position_id=evidence.accountable_position_id,
            expected_outcome=(
                "Complete, reconciled production coverage for every scheduled operating "
                "date and a rerun that can validate or withdraw the performance condition."
            ),
            review_horizon="Within one business day",
            decision_required=True,
            so_what_dimensions=(
                "causal understanding",
                "ownership",
                "timing",
                "confidence",
            ),
        )
    else:
        material_gap = (
            potential.realization_rate is not None
            and potential.realization_rate < policy.material_realization_rate
        )
        condition = MaterialCondition(
            condition_type=(
                ConditionType.OPPORTUNITY
                if material_gap
                else ConditionType.CONSTRAINT
            ),
            state=(
                ConditionState.MANAGE
                if material_gap
                else ConditionState.OBSERVE
            ),
            title=(
                "Capacity potential is not yet governed True Potential"
                if tp_limitations
                else "Actual performance evaluated against True Potential"
            ),
            evidence=(
                f"Actual production is {evidence.actual_frh:,.1f} FRH.",
                f"Capacity potential is {capacity_frh:,.1f} FRH.",
            ),
            materiality=(f"The capacity-based FRH gap is {frh_gap:,.1f}.",),
            consequence=(
                "Performance correction remains constrained by the stated True "
                "Potential limitations."
                if tp_limitations
                else "The supported opportunity is available for management action."
            ),
        )
        diagnosis = CausalDiagnosis(
            hypothesis=(
                "The available MVI evidence does not discriminate among demand, "
                "work-content, rate, margin, and Process causes."
            ),
            confidence=DiagnosticConfidence.UNRESOLVED,
            supporting_evidence=(
                "The economic location of the gap is known only at aggregate capacity level.",
            ),
            weakened_explanations=(
                "No detailed Process cause is supported.",
            ),
            unresolved_explanations=(
                "Demand sufficiency",
                "Work-content execution",
                "Rate and margin realization",
            ),
            correction_allowed=False,
        )
        management_position = ManagementPosition(
            attention=(
                AttentionClass.NEED if material_gap else AttentionClass.NICE
            ),
            what_matters=(
                "The capacity gap is measurable, but the causal basis is not yet "
                "sufficient for corrective action."
            ),
            why_it_matters=(
                "A targeted diagnostic is safer than an unsupported operating prescription."
            ),
            position=(
                "Preserve the capacity finding and gather the minimum evidence needed "
                "to discriminate among causes."
            ),
            recommended_intervention=(
                "Validate supported demand and DPO governance, then decompose GP/RO "
                "into volume, Hrs/RO, ELR, and margin evidence."
            ),
            owner_id=evidence.accountable_owner_id,
            owner_position_id=evidence.accountable_position_id,
            expected_outcome=(
                "A supported or explicitly unresolved diagnosis with no invented "
                "Process conclusion."
            ),
            review_horizon="At the next completed evidence refresh",
            decision_required=material_gap,
            so_what_dimensions=(
                "economic understanding",
                "confidence",
                "intervention selection",
            ),
        )

    case_id = (
        f"store-{evidence.legacy_store_id}:service:"
        f"{evidence.period_start.isoformat()}:{evidence.period_end.isoformat()}"
    )
    return VerticalSliceResult(
        case_id=case_id,
        evidence_profile=profile,
        true_potential=potential,
        condition=condition,
        diagnosis=diagnosis,
        management_position=management_position,
        trace={
            "evidence_profile": tuple(
                source.source for source in evidence.sources
            ),
            "true_potential": (
                "team_member.dpo",
                "schedule_entry",
                "financial_inputs",
            ),
            "condition": ("work_log", "schedule_entry", "true_potential"),
            "diagnosis": ("condition", "evidence_profile"),
            "management_position": (
                "diagnosis",
                "condition",
                "true_potential",
            ),
            "policy": (policy.version,),
        },
    )
