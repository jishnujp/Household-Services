from app import db
from datetime import datetime, timezone
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Query


## Reference: https://blog.miguelgrinberg.com/post/implementing-the-soft-delete-pattern-with-flask-and-sqlalchemy


class DeactivateQuery(Query):
    def __init__(self, entities, *args, **kwargs):
        super().__init__(entities, *args, **kwargs)
        # Apply the filter by default on initialization
        self._with_deactivated = False
        self = self.filter_by(is_deactivated=False)

    def with_deactivated(self):
        """Allow including deactivate entries in the query."""
        self._with_deactivated = True
        return self

    def filter(self, *criterion):
        if not self._with_deactivated:
            # Retrieve the entity(model) from column_descriptions
            entity = self.column_descriptions[0]["entity"]
            criterion = criterion + (entity.is_deactivated == False,)
        return super().filter(*criterion)

    def filter_by(self, **kwargs):
        if not self._with_deactivated:
            kwargs["is_deactivated"] = False
        return super().filter_by(**kwargs)

    def all(self):
        """Override .all() to ensure is_deactivated=False is applied by default."""
        if not self._with_deactivated:
            entity = self.column_descriptions[0]["entity"]
            self = self.filter(entity.is_deactivated == False)
        return super().all()

    def first(self):
        """Override .first() to ensure is_deactivated=False is applied by default."""
        if not self._with_deactivated:
            entity = self.column_descriptions[0]["entity"]
            self = self.filter(entity.is_deactivated == False)
        return super().first()

    def count(self):
        """Override .count() to ensure is_deactivated=False is applied by default."""
        if not self._with_deactivated:
            # Retrieve the entity (model) from column_descriptions
            entity = self.column_descriptions[0]["entity"]
            self = self.filter(entity.is_deactivated == False)
        return super().count()


# NOTE: Faced the `TypeError: metaclass conflict` when tried multiple inheritance with `BaseModel` and `ABC`, to make it an abstract class.
# To resolve this issue, used __abstract__ = True to make it an abstract class and skip the creation of the table for this class.
# Reference: https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/api.html#abstract


class BaseModel(db.Model):
    __abstract__ = True
    query_class = DeactivateQuery

    @declared_attr
    def is_deactivated(cls):
        return db.Column(db.Boolean, default=False)

    @declared_attr
    def deactivate_at(cls):
        return db.Column(db.DateTime, nullable=True)

    @declared_attr
    def created_at(cls):
        return db.Column(
            db.DateTime, default=datetime.now(timezone.utc), nullable=False
        )

    @declared_attr
    def updated_at(cls):
        return db.Column(
            db.DateTime,
            default=datetime.now(timezone.utc),
            onupdate=datetime.now(timezone.utc),
            nullable=False,
        )

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()

    def deactivate(self):
        if self.is_deactivated:
            raise Exception("Already deactivated")
        self.is_deactivated = True
        self.deactivate_at = datetime.now(timezone.utc)
        db.session.commit()

    def activate(self):
        if not self.is_deactivated:
            raise Exception("Already activated")
        self.is_deactivated = False
        self.deactivate_at = datetime.now(timezone.utc)
        db.session.commit()
