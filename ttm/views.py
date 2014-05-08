from ttm import app
from models import Post, UserPreferences
from flask import render_template, flash, redirect, url_for, request, g
from flask.ext import wtf
from flask.ext.wtf import validators
from wtforms import TextField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from decorators import login_required
from google.appengine.api import users
from google.appengine.ext import ndb

class PostForm(wtf.Form):
  title = TextField('Title', validators=[DataRequired()])
  content = TextAreaField('Content', validators=[DataRequired()])

@app.before_request
def before_request():
  if users.get_current_user():
    user = users.get_current_user();
    g.loginlogouttext = 'Logout'
    g.loginlogouturl = users.create_logout_url(request.url)
    # Log that the user is logged in.
    key = ndb.Key('UserPreferences', user.user_id())
    preferences = key.get();
    if not preferences:
      userpref = UserPreferences(id = user.user_id())
      userpref.something = 'Tessttting'
      key = userpref.put()
      app.logger.debug(key.id())
  else:
    g.loginlogouttext = 'Login'
    g.loginlogouturl = users.create_login_url(request.url)

@app.route('/posts')
def list_posts():
  posts = Post.all()
  return render_template('list_posts.html', posts=posts)

@app.route('/users')
def list_users():
  userstrack = UserPreferences.query()
  return render_template('list_users.html', userstrack=userstrack)

@app.route('/posts/new', methods = ['GET', 'POST'])
@login_required
def new_post():
  form = PostForm()
  if form.validate_on_submit():
    post = Post(title = form.title.data,
          content = form.content.data,
          author = users.get_current_user())
    post.put()
    flash('Post saved on database.')
    return redirect(url_for('list_posts'))
  return render_template('new_post.html', form=form)