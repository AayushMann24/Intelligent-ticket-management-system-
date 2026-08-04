from app.database.connection import Base

# Import all models so SQLAlchemy registers them
from app.models.user import User
from app.models.ticket import Ticket