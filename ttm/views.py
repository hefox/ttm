from ttm import app
from models import UserPreferences
from flask import render_template, flash, redirect, url_for, request, g
from decorators import login_required
from google.appengine.api import users
from user_preferences import *
from forms import userPreferenceForm

@app.before_request
def before_request():
  if users.get_current_user():
    user = users.get_current_user();
    g.loginlogouttext = 'Logout'
    g.loginlogouturl = users.create_logout_url(request.url)
    # Update location of user
    update_preferences()
  else:
    g.loginlogouttext = 'Login'
    g.loginlogouturl = users.create_login_url(request.url)

@app.route('/users')
def list_users():
  userstrack = UserPreferences.query()
  return render_template('list_users.html', userstrack=userstrack)

@app.route('/users/preferences', methods = ['GET', 'POST'])
@login_required
def user_preferences():
  form = userPreferenceForm()
  if form.validate_on_submit():
    gender = []
    if len(form.gender_multiple.data) > 0:
      gender = [x.strip() for x in form.gender_multiple.data.split(',')]
    if form.gender_male.data:
      gender.append("male")
    if form.gender_female.data:
      gender.append("female")
    app.logger.debug('Updating gender')
    app.logger.debug(gender)
    update_preferences({'gender':gender})
    flash('Preferences updated.')
    return redirect(url_for('list_users'))
  return render_template('user_preferences.html', form=form)
  