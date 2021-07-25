from views import db
from models import Task
from datetime import date
# create the database and the db table
db.create_all()
# insert data
db.session.add(Task("Finish this tutorial", date(2016, 9, 22), 10, 1))
db.session.add(Task("Finish ", date(2016, 10, 3), 10, 1))
# commit the changes
db.session.commit()