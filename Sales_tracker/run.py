from application import app
from db import db

app.app_context().push()
db.init_app(app)
db.create_all()
app.run(port=5000, debug=True)

