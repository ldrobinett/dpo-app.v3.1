import csv
import io
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import WorkLog, TeamMember, Team, ManagedStore
from forms import ReconciliationForm
from datetime import datetime

reconciliation_bp = Blueprint('reconciliation', __name__)

@reconciliation_bp.route("/manage/reconcile", methods=['GET', 'POST'])
@login_required
def reconcile_logs():
    form = ReconciliationForm()
    audit_results = []
    
    if form.validate_on_submit():
        f = form.dms_file.data
        # Use 'latin-1' or 'cp1252' encoding which is common for legacy DMS exports
        stream = io.StringIO(f.stream.read().decode("latin-1"), newline=None)
        csv_input = csv.reader(stream)
        
        # Mapping: Tech Number -> Member Object
        store_techs = TeamMember.query.join(Team).filter(Team.store_id == current_user.store_id).all()
        tech_map = {t.tech_number: t for t in store_techs if t.tech_number}
        
        # Skip Header (Row 0)
        next(csv_input, None)
        
        for row in csv_input:
            if not row or len(row) < 14: continue 
            
            # CDK Format Parsing
            try:
                csv_ro = row[0].strip()
                if not csv_ro: continue 
                
                csv_tech_num = row[4].strip()
                csv_line = row[5].strip() # Line Item (Col 5 / Index 5)
                
                try:
                    csv_sold_hours = float(row[13]) if row[13].strip() else 0.0
                    csv_actual_hours = float(row[12]) if row[12].strip() else 0.0
                except ValueError:
                    continue 
                
                # Parse Date (e.g., "04NOV25")
                csv_date_str = row[1].strip()
                csv_date_obj = None
                clean_date_iso = ""
                if csv_date_str:
                    try:
                        csv_date_obj = datetime.strptime(csv_date_str, '%d%b%y').date()
                        clean_date_iso = csv_date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        pass 
                        
            except IndexError:
                continue

            # Find Tech
            tech = tech_map.get(csv_tech_num)
            
            if tech:
                # Match Log in DB (Match by RO and Line Item if possible, else just RO)
                # Ideally we match RO + Line, but sometimes line items differ (e.g. 'A' vs '01')
                # Let's try strict match first
                query = WorkLog.query.filter_by(team_member_id=tech.id, ro_number=csv_ro)
                if csv_line:
                    # Optional: Filter by line item if you want strict matching
                    # query = query.filter_by(line_item=csv_line)
                    pass
                
                if csv_date_obj:
                    query = query.filter_by(date=csv_date_obj)
                
                # If multiple entries for same RO (e.g. lines A and B), this logic might need 
                # to be smarter (summing them), but for now let's find the first match.
                app_log = query.first()
                
                app_hours = 0.0
                if app_log:
                    app_hours = app_log.flat_rate_hours
                
                # Calc Variance (App - DMS)
                variance = app_hours - csv_sold_hours
                
                status = 'Missing'
                if app_log:
                    if abs(variance) < 0.01: # Float tolerance
                        status = 'Match'
                    elif variance > 0:
                        status = 'Over-reported'
                    else:
                        status = 'Under-reported'
                
                audit_results.append({
                    'tech_id': tech.id,
                    'tech_name': tech.name,
                    'date': clean_date_iso,
                    'ro': csv_ro,
                    'line': csv_line,
                    'dms_hours': csv_sold_hours,
                    'dms_actual': csv_actual_hours,
                    'app_hours': app_hours,
                    'variance': variance,
                    'status': status
                })
            else:
                # Unknown Tech
                audit_results.append({
                    'tech_name': f"Unknown ID {csv_tech_num}",
                    'date': clean_date_iso,
                    'ro': csv_ro,
                    'line': csv_line,
                    'dms_hours': csv_sold_hours,
                    'dms_actual': 0,
                    'app_hours': 0,
                    'variance': -csv_sold_hours,
                    'status': 'Unknown Tech'
                })

        store = db.session.get(ManagedStore, current_user.store_id)
        if store:
            store.tech_hours_audit_timestamp = datetime.utcnow()

        db.session.commit()

    return render_template('reconciliation.html', form=form, results=audit_results, title="Work Log Reconciliation")

@reconciliation_bp.route("/manage/reconcile/add", methods=['POST'])
@login_required
def add_from_audit():
    """AJAX Endpoint to add a missing log from the audit screen"""
    try:
        data = request.json
        
        # Validate date
        log_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        
        new_log = WorkLog(
            team_member_id=int(data.get('tech_id')),
            date=log_date,
            ro_number=data.get('ro'),
            line_item=data.get('line'),
            flat_rate_hours=float(data.get('sold')),
            actual_time=float(data.get('actual')),
            notes="Added via Audit Reconciler"
        )
        
        db.session.add(new_log)
                
        # Update Tech Hours CDK audit timestamp
        store = db.session.get(ManagedStore, current_user.store_id)
        if store:
            store.tech_hours_audit_timestamp = datetime.utcnow()
            db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400