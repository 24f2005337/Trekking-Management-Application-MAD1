from flask import current_app as app 
from flask import render_template, request, redirect, url_for, session, flash


from .models import db, User, StaffProfile, Trek, Booking
from datetime import datetime

@app.route('/')
def home():
    
    if session.get('user_id'):
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session.get('role') == 'staff':
            return redirect(url_for('staff_dashboard'))
        else:
            return redirect(url_for('trekker_dashboard'))
            
    
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'trekker')  # Default role 'trekker'
        contact = request.form.get('contact')

        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('User already exists', 'danger')
            return redirect(url_for('register'))
            
        if role == 'staff':
            new_user = User(
                username=username,
                email=email,
                password=password,
                role='staff',
                is_approved=False  # Staff approval pending rahega
            )
            db.session.add(new_user)
            db.session.commit()

            # FIX HERE: Staff ki jagah StaffProfile use kiya h
            new_staff_profile = StaffProfile(
                user_id=new_user.id,
                contact_details=contact,
                status='Pending'  # Tum chaho to status bhi pending rakh sakti ho
            )
            db.session.add(new_staff_profile)
            db.session.commit()

            flash('Registration submitted! Please wait for Admin approval before logging in.', 'warning')
            return redirect(url_for('login'))
            
        else:
            # Normal Trekker Registration
            new_trekker = User(
                username=username,
                email=email,
                password=password,
                role='trekker',
                is_approved=True  # Trekkers directly login kar sakte hain
            )
            db.session.add(new_trekker)
            db.session.commit()
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        
    return render_template('register.html')
    


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            # 1. Blacklist Check
            if user.is_blacklisted:
                flash('Your account has been blacklisted by the admin!', 'danger')
                return redirect(url_for('login'))
            
            # 2. NEW CHANGED SECTION: Staff Approval Check
            # Agar staff approved nahi hai, toh login nahi karne denge
            if user.role == 'staff' and not getattr(user, 'is_approved', True):
                flash('Your staff account is pending admin approval. Please wait for the admin to activate your account.', 'warning')
                return redirect(url_for('login'))
    
            # Proceed with normal login session creation...
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            flash(f'Welcome back, {user.username}! ', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'staff':
                return redirect(url_for('staff_dashboard'))
            else:
                return redirect(url_for('trekker_dashboard'))
        else:
            flash('Invalid Username ya Password!', 'danger')
            return redirect(url_for('login'))
            
    return render_template('login.html')


# 3. LOGOUT ROUTE
@app.route('/logout')
def logout():
    session.clear()
    flash('logged out successfully!', 'info')
    return redirect(url_for('login'))





# ─── ADMIN DASHBOARD ───
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash('Unauthorized Access!', 'danger')
        return redirect(url_for('login'))
        
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='trekker').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()
    
    # staff_profiles = StaffProfile.query.filter_by(status='Active').all()
    # Jo bhi staff user approved hai, uski profile le aao
    staff_profiles = StaffProfile.query.join(User).filter(User.is_approved == True).all()

    
    search_user = request.args.get('search_user', '').strip()
    search_trek = request.args.get('search_trek', '').strip()

    
    user_query = User.query.filter(User.role != 'admin')
    if search_user:
        if search_user.isdigit():
            user_query = user_query.filter(User.id == int(search_user))
        else:
            user_query = user_query.filter(User.username.like(f"%{search_user}%"))
    users_list = user_query.all()

    # 2. Strict Search Logic for Treks (By Name or ID)
    trek_query = Trek.query
    if search_trek:
        if search_trek.isdigit():
            trek_query = trek_query.filter(Trek.id == int(search_trek))
        else:
            trek_query = trek_query.filter(Trek.name.like(f"%{search_trek}%"))
    treks_list = trek_query.all()

    all_bookings = Booking.query.order_by(Booking.booking_date.desc()).all()

    return render_template(
        'admin_dashboard.html',
        total_treks=total_treks,
        total_users=total_users,
        total_staff=total_staff,
        total_bookings=total_bookings,
        users=users_list,
        treks=treks_list,
        staff_profiles=staff_profiles,
        all_bookings=all_bookings,
        search_user=search_user,
        search_trek=search_trek
    )

@app.route('/admin/approve_staff/<int:user_id>', methods=['POST'])
def approve_staff(user_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403
        
    staff_user = User.query.get_or_404(user_id)
    
    if staff_user and staff_user.role == 'staff':
        # 1. User table me approved status true karo
        staff_user.is_approved = True
        
        # 2. FIX: StaffProfile table me status ko 'Active' karo taaki dropdown me dikhe
        if staff_user.staff_profile:
            staff_user.staff_profile.status = 'Active'
            
        db.session.commit()
        flash(f'Staff member {staff_user.username} has been approved and activated successfully!', 'success')
    else:
        flash('Invalid request.', 'danger')
        
    return redirect(url_for('admin_dashboard'))




# ─── 3. ADMIN SUB-FEATURE: CREATE TREK ───
@app.route('/admin/create_trek', methods=['POST'])
def create_trek():
    if session.get('role') != 'admin': return "Unauthorized", 403
    name = request.form.get('name')
    location = request.form.get('location')
    difficulty = request.form.get('difficulty')
    duration = int(request.form.get('duration'))
    slots = int(request.form.get('slots'))
    staff_id = request.form.get('staff_id')
    
    start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
    
    new_trek = Trek(
        name=name, location=location, difficulty=difficulty, duration=duration,
        available_slots=slots, status='Approved', start_date=start_date, end_date=end_date,
        staff_id=staff_id if staff_id else None

    )
    db.session.add(new_trek)
    db.session.commit()
    
    flash(f'Trek "{name}" successfully created and approved!', 'success')
    return redirect(url_for('admin_dashboard'))


# ─── 4. ADMIN SUB-FEATURE: TOGGLE BLACKLIST (Deactivate User/Staff) ───
@app.route('/admin/toggle_blacklist/<int:user_id>', methods=['POST'])
def toggle_blacklist(user_id):
    if session.get('role') != 'admin': return "Unauthorized", 403
    
    user = User.query.get_or_404(user_id)
    
    if user.role == 'admin':
        flash('Admin cannot blacklist themselves!', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    
    status_msg = "Blacklisted/Deactivated" if user.is_blacklisted else "Re-activated"
    flash(f'Account "{user.username}" status updated to: {status_msg}!', 'info')
    return redirect(url_for('admin_dashboard'))




# ——— ADMIN CONTROL: EDIT TREK DETAILS (FIXED FIELDS ATTRIBUTE) ———
# ——— ADMIN CONTROL: EDIT TREK DETAILS (FIXED FIELDS ATTRIBUTE) ———
@app.route('/admin/edit_trek/<int:trek_id>', methods=['GET', 'POST'])
def edit_trek(trek_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403
        
    trek = Trek.query.get_or_404(trek_id)
    
    if request.method == 'POST':
        trek.name = request.form.get('name')
        trek.location = request.form.get('location')
        trek.difficulty = request.form.get('difficulty')
        trek.duration = int(request.form.get('duration'))
        
        new_slots = int(request.form.get('slots'))
        trek.available_slots = new_slots
        
        # Handle submitted staff_id from dropdown
        submitted_staff_id = request.form.get('staff_id')
        if submitted_staff_id:
            trek.staff_id = int(submitted_staff_id)
        else:
            trek.staff_id = None # Keep Unassigned selected
            
        db.session.commit()
        flash(f'Trek "{trek.name}" details successfully updated!', 'success')
        return redirect(url_for('admin_dashboard') + '#treks-section')
        
    # GET Request FIX: Sirf unhi profiles ko lao jo completely approved hain
    staff_profiles = StaffProfile.query.join(User).filter(User.is_approved == True).all()
    return render_template('edit_trek.html', trek=trek, staff_profiles=staff_profiles)


# ─── ADMIN CONTROL: REMOVE / DELETE TREK ───
@app.route('/admin/delete_trek/<int:trek_id>', methods=['POST'])
def delete_trek(trek_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403
        
    trek = Trek.query.get_or_404(trek_id)
    
    
    Booking.query.filter_by(trek_id=trek.id).delete()
    
    db.session.delete(trek)
    db.session.commit()
    
    flash('Trek route and its linked bookings removed successfully.', 'info')
    return redirect(url_for('admin_dashboard') + '#treks-section')




# ─── 1. TREK STAFF MAIN DASHBOARD ───
@app.route('/staff/dashboard')
def staff_dashboard():
    if session.get('role') != 'staff':
        flash('Unauthorized Access! Please login as Trek Staff.', 'danger')
        return redirect(url_for('login'))
        
    
    user_id = session.get('user_id')
    staff_prof = StaffProfile.query.filter_by(user_id=user_id).first()
    
    if not staff_prof:
        flash('Staff profile records not found!', 'danger')
        return redirect(url_for('login'))
        
    
    assigned_treks = Trek.query.filter_by(staff_id=staff_prof.id).all()
    
    return render_template(
        'staff_dashboard.html',
        profile=staff_prof,
        treks=assigned_treks
    )


# ─── 2. STAFF SUB-FEATURE: UPDATE TREK SLOTS & STATUS ───
@app.route('/staff/update_trek/<int:trek_id>', methods=['POST'])
def update_trek(trek_id):
    if session.get('role') != 'staff': return "Unauthorized", 403
    
    user_id = session.get('user_id')
    staff_prof = StaffProfile.query.filter_by(user_id=user_id).first()
    trek = Trek.query.get_or_404(trek_id)
    
    
    if trek.staff_id != staff_prof.id:
        flash('Security Violation! You are not assigned to this trek.', 'danger')
        return redirect(url_for('staff_dashboard'))
        
    
    new_slots = int(request.form.get('slots'))
    new_status = request.form.get('status')
    
    trek.available_slots = new_slots
    trek.status = new_status
    db.session.commit()
    
    flash(f'Trek "{trek.name}" status and slots successfully updated!', 'success')
    return redirect(url_for('staff_dashboard'))


# ─── 3. STAFF SUB-FEATURE: VIEW PARTICIPANTS LIST ───
@app.route('/staff/trek/<int:trek_id>/participants')
def view_participants(trek_id):
    if session.get('role') != 'staff': return "Unauthorized", 403
    
    user_id = session.get('user_id')
    staff_prof = StaffProfile.query.filter_by(user_id=user_id).first()
    trek = Trek.query.get_or_404(trek_id)
    
    
    if trek.staff_id != staff_prof.id:
        flash('Unauthorized to view this participant registry!', 'danger')
        return redirect(url_for('staff_dashboard'))
        
    
    active_bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
    
    return render_template(
        'trek_participants.html',
        trek=trek,
        bookings=active_bookings
    )

# ─── 1. USER (TREKKER) DASHBOARD WITH FILTERS ───
@app.route('/dashboard')
def trekker_dashboard():
    if session.get('role') != 'trekker':
        flash('Unauthorized Access! Please login as Trekker.', 'danger')
        return redirect(url_for('login'))
        
    user_id = session.get('user_id')
    
    
    filter_location = request.args.get('location', '').strip()
    filter_difficulty = request.args.get('difficulty', '').strip()

    
    trek_query = Trek.query.filter_by(status='Open')

    
    if filter_location:
        trek_query = trek_query.filter(Trek.location.like(f"%{filter_location}%"))
    if filter_difficulty:
        trek_query = trek_query.filter_by(difficulty=filter_difficulty)

    available_treks = trek_query.all()

    
    user_bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()

    return render_template(
        'trekker_dashboard.html',
        treks=available_treks,
        bookings=user_bookings,
        selected_location=filter_location,
        selected_difficulty=filter_difficulty
    )


# ─── 2. TREKKER ACTION: LIVE SLOT BOOKING ───
@app.route('/book_trek/<int:trek_id>', methods=['POST'])
def book_trek(trek_id):
    if session.get('role') != 'trekker': return "Unauthorized", 403
    
    user_id = session.get('user_id')
    trek = Trek.query.get_or_404(trek_id)

    
    if trek.status != 'Open':
        flash('Booking Failed! This trek is currently not accepting registrations.', 'danger')
        return redirect(url_for('trekker_dashboard'))

    
    if trek.available_slots <= 0:
        flash('Booking Failed! Sorry, all slots for this trek are fully booked.', 'danger')
        return redirect(url_for('trekker_dashboard'))

    
    already_booked = Booking.query.filter_by(user_id=user_id, trek_id=trek_id, status='Booked').first()
    if already_booked:
        flash('You have already booked this trek!', 'warning')
        return redirect(url_for('trekker_dashboard'))


    new_booking = Booking(user_id=user_id, trek_id=trek.id, status='Booked')
    trek.available_slots -= 1  
    
    db.session.add(new_booking)
    db.session.commit()

    flash(f'Congratulations! Your slot for "{trek.name}" is successfully confirmed!', 'success')
    return redirect(url_for('trekker_dashboard'))


# ─── 3. TREKKER ACTION: CANCEL BOOKING ───
@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if session.get('role') != 'trekker': return "Unauthorized", 403
    
    user_id = session.get('user_id')
    booking = Booking.query.get_or_404(booking_id)


    if booking.user_id != user_id:
        return "Unauthorized Request", 401

    if booking.status == 'Booked':
        booking.status = 'Cancelled'
        
        booking.trek_details.available_slots += 1
        db.session.commit()
        flash('Trek booking successfully cancelled. Refund/Release initialized.', 'info')
    else:
        flash('This booking cannot be cancelled.', 'warning')

    return redirect(url_for('trekker_dashboard'))