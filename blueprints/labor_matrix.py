from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_required
from extensions import db
from models import LaborGrid, LaborGridRate
from forms import LaborGridForm
from sqlalchemy.orm import joinedload
from sqlalchemy import asc
from datetime import datetime
import math

labor_matrix_bp = Blueprint('labor_matrix', __name__, url_prefix='/labor-matrix')

def _calculate_and_save_rates(grid):
    """Calculates rates based on grid parameters and saves them."""
    LaborGridRate.query.filter_by(grid_id=grid.id).delete()
    
    start_rate = float(grid.starting_rate or 0.0)
    peak_hrs = float(grid.peak_hours or 0.0)
    escalator = float(grid.escalator_percent or 0.0) / 100.0
    return_hrs = float(grid.return_normal_hours or 0.0)
    discount_hrs = float(grid.discount_start_hours) if grid.discount_start_hours is not None else None
    discount_mult = float(grid.discount_percent / 100.0) if grid.discount_percent is not None else None
    peak_rate = start_rate * (1.0 + escalator)

    def calculate_rate(h):
        if h <= 0: return 0.0
        if h <= peak_hrs:
            increase_per_hour = (peak_rate - start_rate) / peak_hrs if peak_hrs > 0 else 0
            return max(start_rate, start_rate + (increase_per_hour * h))
        elif h <= return_hrs:
             if return_hrs == peak_hrs: return start_rate
             decrease_per_hour = (peak_rate - start_rate) / (return_hrs - peak_hrs)
             return max(start_rate, peak_rate - (decrease_per_hour * (h - peak_hrs)))
        elif discount_hrs is None or h < discount_hrs:
             return start_rate
        else: 
             if discount_mult is not None:
                return start_rate * discount_mult
             else:
                return start_rate

    new_rates = []
    max_calc_hours = 20.0
    if discount_hrs is not None:
        max_calc_hours = max(max_calc_hours, discount_hrs + 2.0)
    elif return_hrs is not None:
        max_calc_hours = max(max_calc_hours, return_hrs + 2.0)
    max_calc_hours = math.ceil(max_calc_hours)

    current_h = 0.1
    while current_h <= max_calc_hours:
        h = round(current_h, 1)
        eff_rate = calculate_rate(h)
        new_rates.append(LaborGridRate(grid_id=grid.id, hours=h, effective_rate=eff_rate))
        current_h += 0.1

    if new_rates:
        db.session.add_all(new_rates)
        db.session.commit()
        print(f"Calculated and saved {len(new_rates)} rates for grid {grid.id}")
    else:
        print(f"No rates calculated for grid {grid.id}")


@labor_matrix_bp.route('/')
@login_required
def list_grids():
    grids = LaborGrid.query.order_by(LaborGrid.name).all()
    return render_template('labor_grids.html', title='Labor Grids', grids=grids)

@labor_matrix_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_grid():
    form = LaborGridForm()
    if form.validate_on_submit():
        new_grid = LaborGrid()
        form.populate_obj(new_grid) # Populate all fields from form
        
        db.session.add(new_grid)
        if LaborGrid.query.count() == 1:
            new_grid.is_active = True
        db.session.commit() 
        try:
             _calculate_and_save_rates(new_grid)
             flash(f'Labor Grid "{new_grid.name}" created and rates calculated.', 'success')
        except Exception as e:
             db.session.rollback()
             flash(f'Grid saved, but failed to calculate rates: {str(e)}', 'danger')
             print(f"Error calculating rates for new grid {new_grid.id}: {e}")
        return redirect(url_for('labor_matrix.list_grids'))
    return render_template('create_edit_labor_grid.html', title='Add Labor Grid', form=form)

@labor_matrix_bp.route('/<int:grid_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_grid(grid_id):
    grid = LaborGrid.query.get_or_404(grid_id)
    form = LaborGridForm(obj=grid)
    if form.validate_on_submit():
        form.populate_obj(grid) # Populate all fields from form
        db.session.commit()
        try:
            _calculate_and_save_rates(grid)
            flash(f'Labor Grid "{grid.name}" updated and rates recalculated.', 'success')
        except Exception as e:
            flash(f'Grid updated, but failed to recalculate rates: {str(e)}', 'danger')
            print(f"Error recalculating rates for grid {grid.id}: {e}")
        return redirect(url_for('labor_matrix.list_grids'))
    return render_template('create_edit_labor_grid.html', title=f'Edit Labor Grid: {grid.name}', form=form)

@labor_matrix_bp.route('/<int:grid_id>/delete', methods=['POST'])
@login_required
def delete_grid(grid_id):
    grid = LaborGrid.query.get_or_404(grid_id)
    if grid.is_active:
        flash('Cannot delete the active labor grid. Activate another grid first.', 'danger')
        return redirect(url_for('labor_matrix.list_grids'))
    grid_name = grid.name
    db.session.delete(grid)
    db.session.commit()
    flash(f'Labor Grid "{grid_name}" deleted successfully.', 'success')
    return redirect(url_for('labor_matrix.list_grids'))

@labor_matrix_bp.route('/<int:grid_id>/activate', methods=['POST'])
@login_required
def activate_grid(grid_id):
    grid_to_activate = LaborGrid.query.get_or_404(grid_id)
    # Deactivate all other grids
    LaborGrid.query.filter(LaborGrid.id != grid_id, LaborGrid.is_active == True).update({LaborGrid.is_active: False})
    grid_to_activate.is_active = True
    db.session.commit()
    flash(f'Labor Grid "{grid_to_activate.name}" is now active.', 'success')
    return redirect(url_for('labor_matrix.list_grids'))

@labor_matrix_bp.route('/<int:grid_id>/rates')
@login_required
def list_rates(grid_id):
    grid = LaborGrid.query.options(joinedload(LaborGrid.rates)).get_or_404(grid_id)
    rates = sorted(grid.rates, key=lambda r: r.hours)
    return render_template('edit_labor_grid_rates.html', title=f'Calculated Rates for {grid.name}', grid=grid, rates=rates)


def get_rate_for_hours(target_hours, rates_list):
    """Finds the effective rate by looking up the closest stored hour increment."""
    if not rates_list: return 0.0
    if target_hours <= 0.0: return 0.0
    lookup_hour = round(target_hours * 10) / 10.0
    found_rate = None
    for rate_entry in rates_list:
        if math.isclose(float(rate_entry.hours), lookup_hour):
            found_rate = float(rate_entry.effective_rate)
            break 
    if found_rate is None:
        if lookup_hour < float(rates_list[0].hours):
            return float(rates_list[0].effective_rate)
        else: 
             return float(rates_list[-1].effective_rate)
    return found_rate

@labor_matrix_bp.route('/print')
@login_required
def print_grid():
    active_grid = LaborGrid.query.filter_by(is_active=True).first()
    if not active_grid:
        flash('No active labor grid found to print.', 'warning')
        return redirect(url_for('labor_matrix.list_grids'))

    rates = LaborGridRate.query.filter_by(grid_id=active_grid.id).order_by(asc(LaborGridRate.hours)).all()
    if not rates:
        flash(f'No rates found for the active grid "{active_grid.name}". Please edit the grid to calculate rates.', 'warning')
        return redirect(url_for('labor_matrix.list_grids'))

    calculated_grid = []
    max_hours_stored = max(float(r.hours) for r in rates) if rates else 0
    max_whole_hour = max(math.ceil(max_hours_stored), 5)

    for whole_hour_base in range(0, max_whole_hour):
        row_data = {'whole_hour': float(whole_hour_base), 'charges': []}
        for tenth_int in range(0, 10): # 0.0 to 0.9
            tenth = tenth_int / 10.0
            current_hours = round(float(whole_hour_base) + tenth, 1)
            if current_hours == 0.0:
                 total_charge = 0.0
            else:
                 effective_rate = get_rate_for_hours(current_hours, rates)
                 total_charge = current_hours * effective_rate
            row_data['charges'].append(total_charge)
        calculated_grid.append(row_data)

    current_time = datetime.now()

    return render_template('print_labor_grid.html',
                           title=f'Printable Labor Grid: {active_grid.name}',
                           grid=active_grid,
                           calculated_grid=calculated_grid,
                           print_time=current_time)