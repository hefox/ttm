from google.appengine.api import users
from google.appengine.ext import ndb
from flask import request

from models import UserPreferences


def update_preferences(in_preferences = None, update_location_with_default = True):
  # Fetch the preferences object.
  preferences = get_user_preferences()

  latlong = request.headers.get("X-AppEngine-CityLatLong")
  # This is not set for local development, so set it to random place.
  if update_location_with_default is True and latlong is None:
    latlong = "37.774929,-122.419416"

  # Set the user location if set.
  if latlong is not None:
    preferences.location = ndb.GeoPt(latlong)
  # Add any new preferences to user object.
  if in_preferences is not None:
    for key, value in in_preferences.iteritems():
      setattr(preferences, key, value)
  preferences.put()

def get_user_preferences(user = None):
  if user is None:
    user = users.get_current_user()
  # todo throw exception if not valid user.
  key = ndb.Key('UserPreferences', user.user_id())
  preferences = key.get();
  # If user doesn't exist in database, create it.
  if not preferences:
    preferences = UserPreferences(id = user.user_id())
  return preferences