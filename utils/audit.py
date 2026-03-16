from datetime import datetime
from extensions import db
from models import ManagedStore

def update_audit_timestamp(store_id):

    store = ManagedStore.query.get(store_id)

    if not store:
        return

    store.last_audit_date = datetime.utcnow()

    db.session.commit()
