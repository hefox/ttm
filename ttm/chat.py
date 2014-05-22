from ttm import app
from google.appengine.api import users
from google.appengine.api import channel
from models import Chats, Message
from google.appengine.ext import ndb
import json
from flask import render_template

def get_chat_id(user1, user2):
  if user1.user_id() < user2.user_id():
    return user1.user_id() + '_' + user2.user_id()
  else:
    return user2.user_id() + '_' + user1.user_id()

def get_chat_info(in_user):
  user = users.get_current_user()
  id = get_chat_id(in_user, user)
  token = channel.create_channel(user.user_id() + '_' + id)
  chats = get_chat(id)
  return {'token': token, 'chat_key': id, 'messages': chats.messages};

def get_chat(chat_id):
  key = ndb.Key('Chats', chat_id)
  chats = key.get()
  if not chats:
    chats = Chats(id = chat_id)
  return chats

def set_chat_message(chat_id, user, in_user, message):
  chats = get_chat(chat_id)
  message = Message(
    user_id = user.user_id(),
    message = message,
  )
  chats.messages.append(message)
  chats.put()
  deliver = json.dumps({'message' : render_template('message.html', message=message, user=user)})
  channel.send_message(user.user_id() + '_' + chat_id, deliver)
  deliver = json.dumps({'message' : render_template('message.html', message=message, user=in_user)})
  channel.send_message(in_user.user_id() + '_' + chat_id, deliver)
