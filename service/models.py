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
    reviews = db.relationship(
        "Review",
        order_by="Review.id",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy=True,
    )

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

    def add_review(self, rating, text=""):
        """Validate and save a rating (1-5) with optional review text."""
        logger.info("Adding review to product id=%s", self.id)
        if (
            isinstance(rating, bool)
            or not isinstance(rating, int)
            or not 1 <= rating <= 5
        ):
            raise DataValidationError("Rating must be an integer from 1 to 5")
        if text is None:
            text = ""
        if not isinstance(text, str):
            raise DataValidationError("Review text must be a string")
        try:
            self.reviews.append(Review(rating=rating, text=text.strip()))
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
            "reviews": [review.serialize() for review in self.reviews],
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

    @staticmethod
    def _parse_query_price(value, field_name):
        """Convert an optional price filter to a finite, non-negative Decimal."""
        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
            raise DataValidationError(f"{field_name} must be a valid number")

        try:
            amount = Decimal(str(value))
        except InvalidOperation as error:
            raise DataValidationError(f"{field_name} must be a valid number") from error

        if not amount.is_finite() or amount < 0:
            raise DataValidationError(f"{field_name} must be finite and non-negative")
        return amount

    @classmethod
    def find_by_filters(cls, name=None, min_price=None, max_price=None):
        """Return products matching all supplied name and price filters."""
        minimum = cls._parse_query_price(min_price, "min_price")
        maximum = cls._parse_query_price(max_price, "max_price")

        if minimum is not None and maximum is not None and minimum > maximum:
            raise DataValidationError(
                "min_price must be less than or equal to max_price"
            )

        logger.info(
            "Finding products: name=%s, min_price=%s, max_price=%s",
            name,
            minimum,
            maximum,
        )

        query = cls.query
        if name:
            query = query.filter(cls.name == name)
        if minimum is not None:
            query = query.filter(cls.price >= minimum)
        if maximum is not None:
            query = query.filter(cls.price <= maximum)
        return query


class Review(db.Model):  # pylint: disable=too-few-public-methods
    """A customer's rating and written review of a product."""

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id", ondelete="CASCADE"),
        nullable=False,
    )
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)

    def serialize(self):
        """Return the review as a dictionary."""
        return {"rating": self.rating, "text": self.text}
