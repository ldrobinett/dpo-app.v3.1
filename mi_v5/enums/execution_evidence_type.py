"""Kinds of proof retained for Action execution."""

from enum import Enum


class ExecutionEvidenceType(str, Enum):
    SOURCE_RECONCILIATION = "source_reconciliation"
    SYSTEM_RECORD = "system_record"
    DOCUMENT = "document"
    OBSERVATION = "observation"
    APPROVED_EXCEPTION = "approved_exception"
