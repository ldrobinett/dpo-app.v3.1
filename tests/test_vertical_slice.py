from __future__ import annotations

import unittest
from datetime import date, datetime, timezone

from mi_v5.vertical_slice.contracts import (
    AttentionClass,
    ConditionState,
    EconomicInputs,
    EvidenceQuality,
    SourceReference,
    StorePeriodEvidence,
    TechnicianPotentialInput,
)
from mi_v5.vertical_slice.engine import evaluate_case


def build_evidence(
    *,
    production_dates: tuple[date, ...],
    supported_demand: float | None = None,
) -> StorePeriodEvidence:
    scheduled = tuple(date(2026, 4, day) for day in range(1, 6))
    return StorePeriodEvidence(
        enterprise_id="enterprise-1",
        managed_store_id="store-1",
        department_id="service-1",
        legacy_store_id=1,
        period_start=date(2026, 4, 1),
        period_end=date(2026, 4, 5),
        extracted_at=datetime(2026, 4, 6, tzinfo=timezone.utc),
        technicians=(
            TechnicianPotentialInput(
                technician_id=1,
                dpo=8.0,
                dpo_mode="manual",
                scheduled_dates=scheduled,
                history_frh=80.0,
                history_days=10,
                expected_lift_percent=105.0,
            ),
        ),
        production_dates=production_dates,
        scheduled_operating_dates=scheduled,
        actual_frh=24.0,
        repair_order_count=12,
        actual_mtd_gross=4_000.0,
        actual_mtd_gross_date=max(production_dates, default=None),
        supported_demand_frh=supported_demand,
        economics=EconomicInputs(
            effective_labor_rate=150.0,
            parts_to_labor_ratio=0.8,
            labor_margin=80.0,
            parts_margin=40.0,
            source_scope="customer_pay",
        ),
        accountable_owner_id="manager-1",
        accountable_position_id="position-1",
        sources=(SourceReference("work_log", "test-v1", 12),),
    )


class VerticalSliceTests(unittest.TestCase):
    def test_capacity_and_economic_math_are_reproducible(self) -> None:
        evidence = build_evidence(
            production_dates=tuple(
                date(2026, 4, day) for day in range(1, 6)
            ),
            supported_demand=35.0,
        )

        result = evaluate_case(evidence)

        self.assertEqual(result.true_potential.capacity_frh, 40.0)
        self.assertEqual(result.true_potential.true_potential_frh, 35.0)
        self.assertEqual(result.true_potential.gp_per_frh, 168.0)
        self.assertEqual(
            result.true_potential.true_potential_cp_gp, 5_880.0
        )

    def test_missing_scheduled_dates_become_evidence_condition(self) -> None:
        evidence = build_evidence(
            production_dates=(
                date(2026, 4, 1),
                date(2026, 4, 2),
                date(2026, 4, 3),
            )
        )

        result = evaluate_case(evidence)

        self.assertEqual(
            result.evidence_profile.completeness,
            EvidenceQuality.LIMITED,
        )
        self.assertEqual(result.condition.state, ConditionState.ESCALATE)
        self.assertFalse(result.diagnosis.correction_allowed)
        self.assertEqual(
            result.management_position.attention, AttentionClass.CRITICAL
        )
        self.assertIn(
            "Verify evidence integrity", result.management_position.position
        )

    def test_absent_process_evidence_does_not_create_process_diagnosis(
        self,
    ) -> None:
        evidence = build_evidence(
            production_dates=tuple(
                date(2026, 4, day) for day in range(1, 6)
            ),
            supported_demand=40.0,
        )

        result = evaluate_case(evidence)

        self.assertFalse(result.diagnosis.correction_allowed)
        self.assertIn("does not discriminate", result.diagnosis.hypothesis)
        self.assertIn("process", result.evidence_profile.missing_domains)


if __name__ == "__main__":
    unittest.main()
