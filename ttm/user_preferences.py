from google.appengine.api import users
from google.appengine.ext import ndb
from flask import request
from ttm import app
from models import UserPreferences
from google.appengine.api import search
from datetime import datetime, timedelta


def update_preferences(in_preferences = None, update_location_with_default = True, user = None):
  if user is None:
    user = users.get_current_user()
  # Fetch the preferences object.
  preferences = get_user_preferences(user.user_id())
  old_latlong = preferences.location

  latlong = request.headers.get("X-AppEngine-CityLatLong")
  # This is not set for local development, so set it to random place.
  if update_location_with_default is True and latlong is None:
    latlong = "37.116526,-121.816406"
  # Set the user location if set.
  if latlong is not None:
    preferences.location = ndb.GeoPt(latlong)

  location_updated = not old_latlong or old_latlong is not preferences.location
  update_document = location_updated or in_preferences is not None or not preferences.document_updated or datetime.now() - preferences.document_updated > timedelta(seconds = 600)
  documented_updated = False;
  # Add any new preferences to user object.
  if in_preferences is not None:
    for key, value in in_preferences.iteritems():
      setattr(preferences, key, value)

  # Search API is limited so try to only update as necessary
  # Also why only storing search information here and using NDB for other stuff.
  if update_document:
    latlongsplit = latlong.split(',');
    geopoint = search.GeoPoint(float(latlongsplit[0]), float(latlongsplit[1]))
    fields = [
      search.GeoField(name='location', value=geopoint),
      search.DateField(name='online', value=datetime.now()),
    ]
    # Add any preferences so can filter on it.
    if preferences.interests:
      for interest in preferences.interests:
        fields.append(search.TextField(name='interest', value=interest))
    if preferences.gender:
      for gender in preferences.gender:
        fields.append(search.TextField(name='gender', value=gender))
    user_document = search.Document(
      doc_id = user.user_id(),
      fields = fields
    )
    try:
      index = search.Index(name="user_search")
      # Note that documents recreate so need to include everything.
      index.put(user_document)
      preferences.document_updated = datetime.now()
      documented_updated = True
    except search.Error:
      app.logger.debug('Put failed')

  # Only update on valid cahnges.
  if in_preferences or location_updated or documented_updated:
    preferences.put()
    app.logger.debug('Updated NDB preferences')

def get_user_preferences(user_id = None):
  if user_id is None:
    user = users.get_current_user()
    if user is not None:
      user_id = user.user_id()
  # todo throw exception if not valid user.
  key = ndb.Key('UserPreferences', user_id)
  preferences = key.get();
  # If user doesn't exist in database, create it.
  if not preferences:
    preferences = UserPreferences(id = user_id)
  return preferences
