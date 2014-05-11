from flask.ext import wtf
from flask.ext.wtf import validators
from wtforms import FormField, TextAreaField, BooleanField

class GenderForm(wtf.Form):
  male = BooleanField('Male')
  female = BooleanField('Female')
  multiple = TextAreaField('More', description="Enter comma separated list of genders you identify with.")

class userPreferenceForm(wtf.Form):
  gender = FormField(GenderForm)
  interests = TextAreaField('Interests', description="Enter comma separated list of interests you have.")
  about = TextAreaField('About you', description="Tell us about yourself.")