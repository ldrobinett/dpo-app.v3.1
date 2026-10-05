"""Preview or create canonical V5 scope for one legacy Managed Store.

Targets only the database selected by DATABASE_URL and requires an explicit
expected database name. It does not create Employee or DPO authority records.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from extensions import db
from mi_v5.models.enterprise import Enterprise
from mi_v5.models.managed_store import ManagedStore
from mi_v5.models.department import Department


def bootstrap(
    *,
    expected_database: str,
    legacy_store_id: int,
    enterprise_name: str,
    enterprise_code: str,
    enterprise_slug: str,
    store_code: str,
    apply: bool = False,
) -> dict:
    app = create_app()
    with app.app_context():
        actual_database = db.engine.url.database
        if actual_database != expected_database:
            raise ValueError(
                f"Expected database {expected_database!r}; connected to {actual_database!r}"
            )
        revision = db.session.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one()
        if revision != "e82cd3516d34":
            raise ValueError(f"V5 migration head required; found {revision}")

        legacy = db.session.execute(
            text("SELECT id, name FROM managed_store WHERE id = :store_id"),
            {"store_id": legacy_store_id},
        ).mappings().one_or_none()
        if legacy is None:
            raise ValueError(f"Legacy managed_store {legacy_store_id} not found")
        if legacy["name"].strip() != "Honda Renton":
            raise ValueError("The legacy store identity is not Honda Renton")

        external_reference = f"legacy_managed_store:{legacy_store_id}"
        enterprise = db.session.query(Enterprise).filter_by(
            enterprise_code=enterprise_code.upper()
        ).one_or_none()
        if enterprise and (
            enterprise.name != enterprise_name.strip()
            or enterprise.slug != enterprise_slug.lower()
        ):
            raise ValueError("Existing Enterprise code has different identity fields")

        store = None
        department = None
        if enterprise:
            store = db.session.query(ManagedStore).filter_by(
                enterprise_id=enterprise.id,
                external_reference=external_reference,
            ).one_or_none()
            if store and (
                store.name != legacy["name"].strip()
                or store.store_code != store_code.upper()
            ):
                raise ValueError("Existing canonical store mapping differs")
            if store:
                department = db.session.query(Department).filter_by(
                    enterprise_id=enterprise.id,
                    managed_store_id=store.id,
                    code="SERVICE",
                ).one_or_none()

        result = {
            "mode": "apply" if apply else "preview",
            "database": actual_database,
            "legacy_store_id": legacy_store_id,
            "legacy_store_name": legacy["name"],
            "enterprise": {
                "name": enterprise_name.strip(),
                "code": enterprise_code.upper(),
                "slug": enterprise_slug.lower(),
                "status": "existing" if enterprise else "planned",
            },
            "managed_store": {
                "name": legacy["name"].strip(),
                "code": store_code.upper(),
                "external_reference": external_reference,
                "status": "existing" if store else "planned",
            },
            "department": {
                "name": "Service",
                "code": "SERVICE",
                "status": "existing" if department else "planned",
            },
            "dpo_authority_created": False,
        }
        if not apply:
            db.session.rollback()
            return result

        try:
            if enterprise is None:
                enterprise = Enterprise(
                    name=enterprise_name,
                    enterprise_code=enterprise_code,
                    slug=enterprise_slug,
                    default_timezone="America/Los_Angeles",
                    country_code="US",
                )
                db.session.add(enterprise)
                db.session.flush()
            if store is None:
                store = ManagedStore(
                    enterprise_id=enterprise.id,
                    name=legacy["name"],
                    store_code=store_code,
                    slug="honda-renton",
                    external_reference=external_reference,
                    timezone="America/Los_Angeles",
                    country_code="US",
                    state_province_code="WA",
                    city="Renton",
                    primary_brand="Honda",
                    brands=["Honda"],
                )
                db.session.add(store)
                db.session.flush()
            if department is None:
                department = Department(
                    enterprise_id=enterprise.id,
                    managed_store_id=store.id,
                    name="Service",
                    code="SERVICE",
                    department_type="service",
                )
                db.session.add(department)
                db.session.flush()
            result["enterprise"]["id"] = str(enterprise.id)
            result["managed_store"]["id"] = str(store.id)
            result["department"]["id"] = str(department.id)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-database", required=True)
    parser.add_argument("--legacy-store-id", type=int, required=True)
    parser.add_argument("--enterprise-name", required=True)
    parser.add_argument("--enterprise-code", required=True)
    parser.add_argument("--enterprise-slug", required=True)
    parser.add_argument("--store-code", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    result = bootstrap(**vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
