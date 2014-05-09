from google.appengine.ext import ndb

class UserPreferences(ndb.Expando):
  something = ndb.StringProperty()
  location = ndb.GeoPtProperty
  gender = ndb.StringProperty(repeated=True)
