"""Product persistence and validation for the products service."""

import logging
from decimal import Decimal, InvalidOperation
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger("flask.app")
db = SQLAlchemy()


class DataValidationError(Exception):
    """Raised when product data cannot be validated or persisted."""


class Product(db.Model):
    """A catalog product with an exact decimal price."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    price = db.Column(db.Numeric(asdecimal=True), nullable=False)

    def __repr__(self):
        return f"<Product {self.name} id=[{self.id}]>"

    @staticmethod
    def _validated_fields(name, description, price):
        """Validate fields without modifying an instance or session."""
        if not isinstance(name, str) or not name.strip():
            raise DataValidationError("Product name must be a non-blank string")
        if len(name) > 63:
            raise DataValidationError("Product name must be at most 63 characters")
        if not isinstance(description, str):
            raise DataValidationError("Product description must be a string")
        if isinstance(price, bool) or not isinstance(price, (Decimal, str, int, float)):
            raise DataValidationError("Product price must be a non-negative number")
        try:
            # Convert JSON numbers through their decimal text, not binary expansion.
            amount = Decimal(str(price))
        except InvalidOperation as error:
            raise DataValidationError(
                "Product price must be a valid decimal"
            ) from error
        if not amount.is_finite() or amount < 0:
            raise DataValidationError("Product price must be finite and non-negative")
        return name, description, amount

    def _validate(self):
        """Normalize valid fields before persistence."""
        description = "" if self.description is None else self.description
        self.name, self.description, self.price = self._validated_fields(
            self.name, description, self.price
        )

    def create(self):
        """Validate and save a new product with a database-generated ID."""
        logger.info("Creating product %s", self.name)
        try:
            self._validate()
            self.id = None
            db.session.add(self)
            db.session.commit()
        except (DataValidationError, SQLAlchemyError) as error:
            db.session.rollback()
            raise DataValidationError(str(error)) from error

    def update(self):
        """Validate and persist changes to an existing product."""
        logger.info("Updating product id=%s", self.id)
        try:
            self._validate()
            db.session.commit()
        except (DataValidationError, SQLAlchemyError) as error:
            db.session.rollback()
            raise DataValidationError(str(error)) from error

    def delete(self):
        """Delete this product and commit the change."""
        logger.info("Deleting product id=%s", self.id)
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as error:
            db.session.rollback()
            raise DataValidationError(str(error)) from error

    def serialize(self):
        """Return product fields, using a decimal string for JSON precision."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": str(self.price),
        }

    def deserialize(self, data):
        """Load validated fields from a dictionary without replacing the ID."""
        if not isinstance(data, dict):
            raise DataValidationError("Product data must be a dictionary")
        try:
            fields = self._validated_fields(
                data["name"], data.get("description", ""), data["price"]
            )
        except KeyError as error:
            raise DataValidationError(
                "Missing product field: " + error.args[0]
            ) from error
        self.name, self.description, self.price = fields
        return self

    @classmethod
    def all(cls):
        """Return all products, or an empty list."""
        logger.info("Listing products")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Return a product by ID, or None when it does not exist."""
        logger.info("Finding product id=%s", by_id)
        return db.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Return a query matching the exact product name."""
        logger.info("Finding products named %s", name)
        return cls.query.filter(cls.name == name)
