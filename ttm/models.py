from google.appengine.ext import ndb

class UserPreferences(ndb.Expando):
  location = ndb.GeoPtProperty
  gender = ndb.StringProperty(repeated=True)
  interests = ndb.StringProperty(repeated=True)
  about = ndb.StringProperty(default='')
  user = ndb.UserProperty(auto_current_user_add=True)
  updated = ndb.DateTimeProperty(auto_now=True)
  created = ndb.DateTimeProperty(auto_now_add=True)
  document_updated = ndb.DateTimeProperty()


class Message(ndb.Model):
  user_id = ndb.StringProperty()
  message =  ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)

class Chats(ndb.Model):
  chat_id = ndb.StringProperty()
  messages = ndb.StructuredProperty(Message, repeated=True)