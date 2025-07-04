from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.db_models import db, User, PredictionLog

def register_auth_routes(app):
    # Signup route
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']

            if User.query.filter_by(email=email).first():
                flash("Email already exists", "error")
                return redirect(url_for('signup'))

            hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(email=email, username=username, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()

            flash("Account created successfully. Please login.", "success")
            return redirect(url_for('login'))

        return render_template('signup.html')

    # Login route
    @app.route('/login', methods=['GET', 'POST'], endpoint='login')
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()

            if user and check_password_hash(user.password, password):
                login_user(user)
                flash("Login successful", "success")
                return redirect(url_for('home'))
            else:
                flash("Invalid email or password", "error")
                return redirect(url_for('login'))

        return render_template('login.html')

    # Logout route
    @app.route('/logout', endpoint='logout')
    @login_required
    def logout():
        logout_user()
        session.clear()
        flash("You have been logged out", "success")
        return redirect(url_for('login'))

    # Prediction logs
    @app.route('/logs')
    @login_required
    def logs():
        user_logs = PredictionLog.query.filter_by(user_id=current_user.id).order_by(PredictionLog.timestamp.desc()).all()
        return render_template('logs.html', logs=user_logs)
