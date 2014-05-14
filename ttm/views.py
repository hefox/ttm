from ttm import app
from models import UserPreferences
from flask import render_template, flash, redirect, url_for, request, g
from decorators import login_required
from google.appengine.api import users
from user_preferences import *
from forms import userPreferenceForm
from helpers import *

@app.before_request
def before_request():
  if users.get_current_user():
    user = users.get_current_user();
    g.loginlogouttext = 'Logout'
    g.loginlogouturl = users.create_logout_url(request.url)
    g.user_is_logged_in = True
    # Update location of user
    update_preferences()
  else:
    g.user_is_logged_in  = False
    g.loginlogouttext = 'Login'
    g.loginlogouturl = users.create_login_url(request.url)

@app.route('/')
@app.route('/users')
@login_required
def list_users():


  userslist = UserPreferences.query()
  # Filter by gender from url.
  if request.args.get('gender'):
    userslist = userslist.filter(UserPreferences.gender == request.args.get('gender'))
  # Filter by interests from url.
  if request.args.get('interest'):
    userslist = userslist.filter(UserPreferences.interests == request.args.get('interest'))
  return render_template('list_users.html', userslist=userslist)

@app.route('/genders')
@login_required
def list_genders():
  genders_all = UserPreferences.query(projection=["gender"], distinct=True)
  genders = []
  for gender in genders_all:
    genders.append(gender.gender[0])
  return render_template('list_genders.html', genders=genders)

@app.route('/interests')
@login_required
def list_interests():
  interests_all = UserPreferences.query(projection=["interests"], distinct=True)
  interests = []
  for interest in interests_all:
    interests.append(interest.interests[0])
  return render_template('list_interests.html', interests=interests)

@app.route('/users/preferences', methods = ['GET', 'POST'])
@login_required
def user_preferences():
  preferences = get_user_preferences()
  # Parse user's current gender settings.
  gender = preferences.gender[:]
  male_default = False
  female_default = False
  if gender:
    if 'male' in gender:
      index = gender.index('male')
      del gender[index]
      male_default = True
    if 'female' in gender:
      index = gender.index('female')
      del gender[index]
      female_default = True
  form = userPreferenceForm(gender = {'multiple' : ', '.join(gender), 'male' : male_default, 'female' : female_default}, about = preferences.about, interests = ', '.join(preferences.interests))
  if form.validate_on_submit():
    gender = []
    if len(form.gender.multiple.data) > 0:
      gender = split_csv_string_to_list(form.gender.multiple.data)
    if form.gender.male.data:
      gender.append("male")
    if form.gender.female.data:
      gender.append("female")
    update_preferences({'gender':gender, 'about' : form.about.data, 'interests' : split_csv_string_to_list(form.interests.data)})
    flash('Preferences updated.')
    return redirect(url_for('list_users'))
  return render_template('user_preferences.html', form=form)
  