import csv
import io
import time
from datetime import datetime, date, timedelta
import calendar
from flask import Blueprint, render_template, url_for, flash, redirect, request, make_response
from flask_login import login_required, current_user
from extensions import db, bcrypt
from models import OnboardingTicket, User, FinancialInputs, Team, TeamMember, ASM, ScheduleEntry
from forms import OnboardingForm, StoreSettingsForm, BulkTeamUploadForm

onboarding_bp = Blueprint('onboarding', __name__)

# ==========================================
# 1. ADMIN & SETUP ROUTES
# ==========================================

@onboarding_bp.route("/admin/generate_invite", methods=['GET', 'POST'])
# @login_required (Add this later to protect it)
def generate_invite():
    email = request.args.get('email')
    if not email:
        return "Please provide an email param", 400
        
    ticket = OnboardingTicket(email=email)
    db.session.add(ticket)
    db.session.commit()
    
    link = url_for('onboarding.setup_store', token=ticket.token, _external=True)
    return f"Send this link to the manager: <br> <a href='{link}'>{link}</a>"

@onboarding_bp.route("/setup/<token>", methods=['GET', 'POST'])
def setup_store(token):
    ticket = OnboardingTicket.query.filter_by(token=token).first_or_404()
    
    if ticket.is_used:
        flash('This setup link has already been used.', 'warning')
        return redirect(url_for('auth.login'))
        
    form = OnboardingForm()
    
    if form.validate_on_submit():
        # 1. Create User
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_store_id = int(time.time()) 
        
        user = User(
            username=form.username.data,
            password=hashed_password,
            store_id=new_store_id
        )
        db.session.add(user)
        db.session.flush() 
        
        # 2. Create Main Team
        main_team = Team(name=form.store_name.data, store_id=new_store_id)
        db.session.add(main_team)
        
        # 3. Create Financial Inputs
        fin_inputs = FinancialInputs(
            user_id=user.id,
            effective_labor_rate=form.elr.data,
            parts_to_labor_ratio=form.parts_to_labor.data,
            labor_margin=form.labor_margin.data,
            parts_margin=form.parts_margin.data,
            cp_effective_labor_rate=form.cp_elr.data,
            cp_parts_to_labor_ratio=form.cp_parts_to_labor.data,
            cp_labor_margin=form.cp_labor_margin.data,
            cp_parts_margin=form.cp_parts_margin.data,
            bays_with_lifts=form.bays_with_lifts.data,
            bays_without_lifts=form.bays_without_lifts.data,
            other_ro_gross=form.other_ro_gross.data,
            unapplied_time_cost=form.unapplied_time_cost.data,
            parts_retail_gross=form.parts_retail_gross.data,
            wholesale_gross=form.wholesale_gross.data,
            parts_inventory_adjust=form.parts_inventory_adjust.data,
            parts_allowance=form.parts_allowance.data,
            purchase_discounts=form.purchase_discounts.data,
            parts_fill_rate=form.parts_fill_rate.data,
            parts_turn_rate=form.parts_turn_rate.data
        )
        db.session.add(fin_inputs)
        
        # 4. Close Ticket
        ticket.is_used = True
        db.session.commit()
        
        flash('Store setup complete! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('onboarding_worksheet.html', form=form, title='Dealership Setup Worksheet')

@onboarding_bp.route("/manage/initial_setup", methods=['GET', 'POST'])
@login_required
def review_setup():
    form = StoreSettingsForm()
    
    # Fetch Data
    main_team = Team.query.filter_by(store_id=current_user.store_id).first()
    fin_inputs = FinancialInputs.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'GET':
        # Pre-fill Form
        if main_team:
            form.store_name.data = main_team.name
        
        if fin_inputs:
            form.elr.data = fin_inputs.effective_labor_rate
            form.parts_to_labor.data = fin_inputs.parts_to_labor_ratio
            form.labor_margin.data = fin_inputs.labor_margin
            form.parts_margin.data = fin_inputs.parts_margin
            form.cp_elr.data = fin_inputs.cp_effective_labor_rate
            form.cp_parts_to_labor.data = fin_inputs.cp_parts_to_labor_ratio
            form.cp_labor_margin.data = fin_inputs.cp_labor_margin
            form.cp_parts_margin.data = fin_inputs.cp_parts_margin
            form.bays_with_lifts.data = fin_inputs.bays_with_lifts
            form.bays_without_lifts.data = fin_inputs.bays_without_lifts
            form.other_ro_gross.data = fin_inputs.other_ro_gross
            form.unapplied_time_cost.data = fin_inputs.unapplied_time_cost
            form.parts_retail_gross.data = fin_inputs.parts_retail_gross
            form.wholesale_gross.data = fin_inputs.wholesale_gross
            form.parts_inventory_adjust.data = fin_inputs.parts_inventory_adjust
            form.parts_allowance.data = fin_inputs.parts_allowance
            form.purchase_discounts.data = fin_inputs.purchase_discounts
            form.parts_fill_rate.data = fin_inputs.parts_fill_rate
            form.parts_turn_rate.data = fin_inputs.parts_turn_rate

    if form.validate_on_submit():
        # Save Changes
        if main_team:
            main_team.name = form.store_name.data
        
        if not fin_inputs:
            fin_inputs = FinancialInputs(user_id=current_user.id)
            db.session.add(fin_inputs)
            
        fin_inputs.effective_labor_rate = form.elr.data
        fin_inputs.parts_to_labor_ratio = form.parts_to_labor.data
        fin_inputs.labor_margin = form.labor_margin.data
        fin_inputs.parts_margin = form.parts_margin.data
        fin_inputs.cp_effective_labor_rate = form.cp_elr.data
        fin_inputs.cp_parts_to_labor_ratio = form.cp_parts_to_labor.data
        fin_inputs.cp_labor_margin = form.cp_labor_margin.data
        fin_inputs.cp_parts_margin = form.cp_parts_margin.data
        fin_inputs.bays_with_lifts = form.bays_with_lifts.data
        fin_inputs.bays_without_lifts = form.bays_without_lifts.data
        fin_inputs.other_ro_gross = form.other_ro_gross.data
        fin_inputs.unapplied_time_cost = form.unapplied_time_cost.data
        fin_inputs.parts_retail_gross = form.parts_retail_gross.data
        fin_inputs.wholesale_gross = form.wholesale_gross.data
        fin_inputs.parts_inventory_adjust = form.parts_inventory_adjust.data
        fin_inputs.parts_allowance = form.parts_allowance.data
        fin_inputs.purchase_discounts = form.purchase_discounts.data
        fin_inputs.parts_fill_rate = form.parts_fill_rate.data
        fin_inputs.parts_turn_rate = form.parts_turn_rate.data
        
        db.session.commit()
        flash('Store settings updated successfully.', 'success')
        return redirect(url_for('onboarding.review_setup'))

    return render_template('store_settings.html', form=form, title='Initial Setup Review')

# ==========================================
# 2. BULK TEAM UPLOAD ROUTES
# ==========================================

@onboarding_bp.route("/onboarding/download_sample", methods=['GET'])
@login_required
def download_sample_csv():
    """Generates a sample CSV file for the user to fill out."""
    header = [
        'Type', 'Name', 'Number', 'Team', 'Level', 
        '10_Wk_FRH', '10_Wk_Days_Off',
        'Work_Days', 'Start_Time', 'End_Time', 'Lunch_Start', 'Lunch_End'
    ]
    
    rows = [
        ['ASM', 'John Advisor', '101', 'Blue Team', '', '', '', 'Mon;Tue;Wed;Thu;Fri', '07:00', '16:00', '12:00', '13:00'],
        ['Tech', 'Mike Mechanic', '1101', 'Blue Team', 'A', '450.0', '2', 'Tue;Wed;Thu;Fri;Sat', '08:00', '17:00', '12:00', '13:00'],
        ['Tech', 'Sarah Service', '1102', 'Red Team', 'B', '380.5', '0', '', '', '', '', '']
    ]
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(header)
    cw.writerows(rows)
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=team_upload_template.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@onboarding_bp.route("/onboarding/team_upload", methods=['GET', 'POST'])
@login_required
def team_upload():
    form = BulkTeamUploadForm()
    
    if form.validate_on_submit():
        f = form.csv_file.data
        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        
        # Skip header
        next(csv_input, None)
        
        count_created = 0
        
        today = date.today()
        start_date = date(today.year, today.month, 1)
        last_day = calendar.monthrange(today.year, today.month)[1]
        end_date = date(today.year, today.month, last_day)
        
        def parse_time(t_str):
            try:
                if t_str and ':' in t_str:
                    return datetime.strptime(t_str.strip(), '%H:%M').time()
            except ValueError:
                pass
            return None

        def parse_days(d_str):
            if not d_str: return None
            d_str = d_str.lower()
            target_ints = []
            days_map = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}
            for day_name, day_int in days_map.items():
                if day_name in d_str:
                    target_ints.append(day_int)
            return target_ints

        for row in csv_input:
            if not row: continue
            
            try:
                row_type = row[0].strip().upper()
                name = row[1].strip()
                number = row[2].strip()
                team_name = row[3].strip()
            except IndexError:
                continue 

            team = Team.query.filter_by(name=team_name, store_id=current_user.store_id).first()
            if not team:
                team = Team(name=team_name, store_id=current_user.store_id)
                db.session.add(team)
                db.session.flush() 
            
            person = None
            
            if 'ASM' in row_type:
                existing = ASM.query.filter_by(asm_number=number, store_id=current_user.store_id).first()
                if not existing:
                    person = ASM(
                        name=name,
                        asm_number=number,
                        team_id=team.id,
                        store_id=current_user.store_id
                    )
                    db.session.add(person)
                
            elif 'TECH' in row_type:
                level = row[4].strip() if len(row) > 4 else ''
                raw_frh = float(row[5]) if len(row) > 5 and row[5] else 0.0
                days_off = int(row[6]) if len(row) > 6 and row[6] else 0
                
                total_work_days = 50 - days_off
                calc_dpo = 0.0
                if total_work_days > 0:
                    calc_dpo = raw_frh / total_work_days
                
                existing = TeamMember.query.filter_by(tech_number=number, team_id=team.id).first()
                if not existing:
                    person = TeamMember(
                        name=name,
                        tech_number=number,
                        team_id=team.id,
                        tech_level=level,
                        dpo_calculation_mode='manual',
                        daily_production_objective=round(calc_dpo, 1),
                        hist_frh_total=raw_frh,
                        hist_days_in_period=50,
                        hist_vacation_days=days_off
                    )
                    db.session.add(person)
            
            db.session.flush() 
            
            if person and hasattr(person, 'id'):
                csv_days = parse_days(row[7]) if len(row) > 7 else None
                work_days = csv_days if csv_days else [0, 1, 2, 3, 4] 
                
                s_time = parse_time(row[8]) if len(row) > 8 else form.default_start_time.data
                e_time = parse_time(row[9]) if len(row) > 9 else form.default_end_time.data
                l_start = parse_time(row[10]) if len(row) > 10 else form.default_lunch_start.data
                l_end = parse_time(row[11]) if len(row) > 11 else form.default_lunch_end.data
                
                if isinstance(person, TeamMember):
                    current_day = start_date
                    while current_day <= end_date:
                        if current_day.weekday() in work_days:
                            exists = ScheduleEntry.query.filter_by(team_member_id=person.id, date=current_day).first()
                            if not exists:
                                entry = ScheduleEntry(
                                    team_member_id=person.id,
                                    date=current_day,
                                    start_time=s_time,
                                    end_time=e_time,
                                    lunch_start=l_start,
                                    lunch_end=l_end,
                                    schedule_type='WORK'
                                )
                                db.session.add(entry)
                        current_day += timedelta(days=1)

            count_created += 1
            
        db.session.commit()
        flash(f'Successfully imported {count_created} rows and generated schedules!', 'success')
        return redirect(url_for('teams.teams')) 
        
    return render_template('onboarding_team_upload.html', form=form, title='Bulk Team Upload')