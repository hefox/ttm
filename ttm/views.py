from ttm import app
from models import UserPreferences, Message, Chats
from flask import render_template, flash, redirect, url_for, request, g, abort
from decorators import login_required
from google.appengine.api import users
from user_preferences import *
from forms import userPreferenceForm
from google.appengine.api.search import *
from helpers import *
from chat import *
import string

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
  index = search.Index(name="user_search")

  # Build the SortOptions with 2 sort keys
  sort_opts = search.SortOptions(expressions=[search.SortExpression(expression='distance(geopoint(37.774929,-122.419416), location)', direction=SortExpression.ASCENDING, default_value=0)])

  # Build the QueryOptions
  query_options = search.QueryOptions(
    limit=25,
    returned_fields=['location', 'online', 'interest'],
    sort_options= sort_opts
  )
  # Create the query string, limit by gender and interest.
  query_string = ''
  if request.args.get('gender'):
    query_string = 'gender = "%s"' % request.args.get('gender').replace('"', '').replace('\\', '')
  # Filter by interests from url.
  if request.args.get('interest'):
    if (query_string):
      query_string = query_string + ' && '
    query_string = query_string + 'interest = "%s"' % request.args.get('interest').replace('"', '').replace('\\', '')

  query = search.Query(query_string=query_string, options=query_options)
  userslist = []
  try:
    results = index.search(query)
    for scored_document in results:
      userslist.append(get_user_preferences(scored_document.doc_id))

  except search.Error:
    app.logger.debug('Search failed')

  return render_template('list_users.html', userslist=userslist)

@app.route('/users/<userid>')
@login_required
def show_user_profile(userid):
  user = get_user_preferences(userid, False)
  if user is not None:
    chat_info = get_chat_info(user.user)
    return  render_template('user.html', current_user = users.get_current_user(), user=user, token = chat_info['token'], chat_key = chat_info['chat_key'], messages = chat_info['messages'])
  else:
    abort(404)

@app.route('/message', methods = ['GET', 'POST'])
@login_required
def record_message():
  user_id = request.form['uid']
  message = request.form['message']
  if not user_id or not message:
    abort(404)
  preferences = get_user_preferences(user_id, False)
  in_user = preferences.user
  user = users.get_current_user()
  if user is None or in_user is None:
    abort(404)
  chat_id = get_chat_id(in_user, user)
  set_chat_message(chat_id, user, in_user, message)
  return 'recorded'

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
  