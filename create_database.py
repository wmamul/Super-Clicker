import sqlalchemy
import app.database
from app.database import models

models.Base.metadata.create_all(app.database.engine)
