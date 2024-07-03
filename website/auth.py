from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import sqlalchemy
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('Email does not exist', category='error')
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash('Invalid Email', category='error')
        elif len(first_name) < 1:
            flash('Invalid First name', category='error')
        elif password1 != password2:
            flash("Passwords don't match", category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 chars', category='error')
        else:
            new_user = User(email=email, first_name=first_name, 
                    password=generate_password_hash(password1, method='pbkdf2:sha256'))
            try:
                db.session.add(new_user)
                db.session.commit()
            except sqlalchemy.exc.IntegrityError: 
                flash("duplicate email", category='error')
            else:
                login_user(new_user, remember=True)
                flash('Account created!', category='success')
                return redirect(url_for('views.home'))
    return render_template("sign_up.html", user=current_user)
