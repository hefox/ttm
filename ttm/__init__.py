from flask import Flask
import settings

app = Flask('ttm')
app.config.from_object('ttm.settings')

import views