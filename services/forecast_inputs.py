"""Shared forecast assumptions; legacy user rows are never changed."""
from types import SimpleNamespace
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import FinancialInputs, StoreForecastInputs, User

FIELDS = (
    'effective_labor_rate', 'parts_to_labor_ratio', 'labor_margin', 'parts_margin',
    'other_ro_gross', 'unapplied_time_cost', 'wholesale_gross', 'parts_retail_gross',
    'parts_inventory_adjust', 'parts_allowance', 'purchase_discounts',
)

class ForecastConflict(ValueError):
    pass


def legacy_candidates(store_id):
    return (db.session.query(FinancialInputs, User.username)
            .join(User, FinancialInputs.user_id == User.id)
            .filter(User.store_id == store_id).order_by(User.id).all())


def values_from(row):
    return {field: getattr(row, field, None) for field in FIELDS}


def as_inputs(row):
    return SimpleNamespace(**row.values) if row else None


def stage_inputs(store_id, user_id, expected_version, values):
    """Stage optimistic update in caller transaction; never commit separately."""
    if expected_version == 0:
        if db.session.get(StoreForecastInputs, store_id) is not None:
            raise ForecastConflict('Another user saved first. Reload and review their inputs.')
        row = StoreForecastInputs(store_id=store_id, values=values,
                                  version=1, updated_by=user_id)
        db.session.add(row)
        try:
            db.session.flush()
        except IntegrityError as exc:
            db.session.rollback()
            raise ForecastConflict('Another user saved first. Reload and review their inputs.') from exc
    else:
        count = (StoreForecastInputs.query.filter_by(store_id=store_id, version=expected_version)
                 .update({'values': values, 'version': expected_version + 1,
                          'updated_by': user_id, 'updated_at': datetime.now(timezone.utc)}, synchronize_session=False))
        if count != 1:
            db.session.rollback()
            raise ForecastConflict('Forecast inputs changed since this page opened. Reload before saving.')
    return SimpleNamespace(**values)
