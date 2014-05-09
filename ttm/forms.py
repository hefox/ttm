from ttm import app
from flask.ext import wtf
from flask.ext.wtf import validators
from wtforms import TextField, BooleanField
from wtforms.validators import DataRequired
from user_preferences import *

class userPreferenceForm(wtf.Form):
  preferences = get_user_preferences()
  gender = preferences.gender[:]
  male_default = False
  female_default = False
  app.logger.debug(gender)
  if gender:
    if 'male' in gender:
      index = gender.index('male')
      del gender[index]
      male_default = True
    if 'female' in gender:
      index = gender.index('female')
      del gender[index]
      female_default = True

  app.logger.debug(','.join(gender))
  gender_male = BooleanField('Male', default = male_default)
  gender_female = BooleanField('Female', default = female_default)
  gender_multiple = TextField('Gender (Free Form)', description="Enter comma separated list of genders you identify with.", default = ','.join(gender))