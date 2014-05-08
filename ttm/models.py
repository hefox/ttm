from google.appengine.ext import db
from google.appengine.ext import ndb

class Post(db.Model):
  title = db.StringProperty(required = True)
  content = db.TextProperty(required = True)
  when = db.DateTimeProperty(auto_now_add = True)
  author = db.UserProperty(required = True)

class UserPreferences(ndb.Expando):
  something = ndb.StringProperty()
