from app import db
from app.models.base_model import BaseModel


class Service(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Integer, nullable=False)

    professionals = db.relationship(
        "ProfessionalDetails", back_populates="service", lazy="select"
    )

    def __repr__(self):
        return f"<Service {self.id}: {self.name}>"
