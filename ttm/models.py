from google.appengine.ext import ndb

class UserPreferences(ndb.Expando):
  location = ndb.GeoPtProperty
  gender = ndb.StringProperty(repeated=True)
  interests = ndb.StringProperty(repeated=True)
  about = ndb.StringProperty(default='')
  user = ndb.UserProperty(auto_current_user_add=True)

