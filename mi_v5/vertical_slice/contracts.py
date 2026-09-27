"""Typed contracts for the first MI v5 end-to-end implementation proof."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any


class EvidenceQuality(str, Enum):
    SUFFICIENT = "sufficient"
    LIMITED = "limited"
    INSUFFICIENT = "insufficient"


class ConditionState(str, Enum):
    NORMAL = "normal"
    OBSERVE = "observe"
    MANAGE = "manage"
    INTERVENE = "intervene"
    ESCALATE = "escalate"
    CRITICAL = "critical"


class ConditionType(str, Enum):
    CONSTRAINT = "constraint"
    RISK = "risk"
    OPPORTUNITY = "opportunity"


class DiagnosticConfidence(str, Enum):
    SUPPORTED = "supported"
    PROBABLE = "probable"
    UNRESOLVED = "unresolved"


class AttentionClass(str, Enum):
    CRITICAL = "critical"
    NEED = "need"
    NICE = "nice"
    NONE = "none"


@dataclass(frozen=True)
class SourceReference:
    source: str
    query_version: str
    record_count: int
    latest_observed_date: date | None = None
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class TechnicianPotentialInput:
    technician_id: int
    dpo: float
    dpo_mode: str
    scheduled_dates: tuple[date, ...]
    history_frh: float | None
    history_days: int | None
    expected_lift_percent: float | None


@dataclass(frozen=True)
class EconomicInputs:
    effective_labor_rate: float | None
    parts_to_labor_ratio: float | None
    labor_margin: float | None
    parts_margin: float | None
    source_scope: str


@dataclass(frozen=True)
class StorePeriodEvidence:
    enterprise_id: str
    managed_store_id: str
    department_id: str
    legacy_store_id: int
    period_start: date
    period_end: date
    extracted_at: datetime
    technicians: tuple[TechnicianPotentialInput, ...]
    production_dates: tuple[date, ...]
    scheduled_operating_dates: tuple[date, ...]
    actual_frh: float
    repair_order_count: int
    actual_mtd_gross: float | None
    actual_mtd_gross_date: date | None
    supported_demand_frh: float | None
    economics: EconomicInputs
    accountable_owner_id: str | None
    accountable_position_id: str | None
    sources: tuple[SourceReference, ...]


@dataclass(frozen=True)
class EvidenceDepthProfile:
    breadth: tuple[str, ...]
    missing_domains: tuple[str, ...]
    granularity: tuple[str, ...]
    historical_depth_days: int
    frequency: str
    freshness_days: int | None
    completeness: EvidenceQuality
    continuity_gap_dates: tuple[date, ...]
    reliability: EvidenceQuality
    scope: tuple[str, ...]
    known: tuple[str, ...]
    inferred: tuple[str, ...]
    unknown: tuple[str, ...]


@dataclass(frozen=True)
class TruePotentialResult:
    method_version: str
    capacity_frh: float
    supported_demand_frh: float | None
    true_potential_frh: float
    validation_status: EvidenceQuality
    gp_per_frh: float | None
    true_potential_cp_gp: float | None
    actual_frh: float
    realization_rate: float | None
    frh_gap: float
    estimated_cp_gp_gap: float | None
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class MaterialCondition:
    condition_type: ConditionType
    state: ConditionState
    title: str
    evidence: tuple[str, ...]
    materiality: tuple[str, ...]
    consequence: str


@dataclass(frozen=True)
class CausalDiagnosis:
    hypothesis: str
    confidence: DiagnosticConfidence
    supporting_evidence: tuple[str, ...]
    weakened_explanations: tuple[str, ...]
    unresolved_explanations: tuple[str, ...]
    correction_allowed: bool


@dataclass(frozen=True)
class ManagementPosition:
    attention: AttentionClass
    what_matters: str
    why_it_matters: str
    position: str
    recommended_intervention: str
    owner_id: str | None
    owner_position_id: str | None
    expected_outcome: str
    review_horizon: str
    decision_required: bool
    so_what_dimensions: tuple[str, ...]


@dataclass(frozen=True)
class VerticalSliceResult:
    case_id: str
    evidence_profile: EvidenceDepthProfile
    true_potential: TruePotentialResult
    condition: MaterialCondition
    diagnosis: CausalDiagnosis
    management_position: ManagementPosition
    trace: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe representation without losing enum meaning."""

        def convert(value: Any) -> Any:
            if isinstance(value, (date, datetime)):
                return value.isoformat()
            if isinstance(value, Enum):
                return value.value
            if isinstance(value, dict):
                return {key: convert(item) for key, item in value.items()}
            if isinstance(value, (list, tuple)):
                return [convert(item) for item in value]
            return value

        return convert(asdict(self))
