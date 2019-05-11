"""
Minimal Flask application with user accounts and login
"""
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from werkzeug.urls import url_parse
import os
import json
import logging

from app import app, db
from app.models import User
from app.email import send_password_reset_email
import config

logger = logging.getLogger(__name__)

@app.route("/", methods=["GET"])
def index():
	return render_template('index.html')

@app.route("/secret", methods=["GET"])
@login_required
def secret():
	return render_template('secret.html')

	
@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == 'POST':
		if current_user.is_authenticated:
			return redirect(url_for('index'))
		user = User.query.filter_by(username=request.form['username']).first()
		if user is None or not user.check_password(request.form['password']):
			flash('Invalid username or password', 'danger')
			return redirect(url_for('login'))
		try:
			r = bool(request.form['remember'])
		except KeyError:
			r = False
		login_user(user, remember=r)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	
	return render_template('login.html')
	
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    
@app.route('/reset_password_request', methods=["GET", "POST"])
def reset_password_request():
	if request.method == "POST":
		user = User.query.filter_by(username=request.form['email']).first()
		if user:
			send_password_reset_email(user)
		flash('Please check your email for instructions on resetting your password',
					 'success')
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	return render_template('reset_password_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	user = User.verify_reset_password_token(token)
	if not user:
		return redirect(url_for('index'))
	if request.method == "POST":
		user.set_password(request.form['password'])
		db.session.commit()
		flash('Your password has been reset.', 'success')
		return redirect(url_for('login'))
	return render_template('reset_password.html')
