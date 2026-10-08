"""
Test Factory to make fake objects for testing
"""

from factory import Factory, Sequence, Faker
from factory.fuzzy import (
    FuzzyChoice,
    FuzzyDecimal,
)  # FuzzyChoice/FuzzyDecimal live in factory.fuzzy
from service.models import Product


class ProductFactory(Factory):
    """Creates fake products for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Product

    id = Sequence(lambda n: n)
    name = FuzzyChoice(
        choices=["Soap", "Shampoo", "Lotion", "Candle", "Paper", "Pen", "Notebook"]
    )
    description = Faker("sentence")
    price = FuzzyDecimal(0.5, 2000.0, precision=2)
    image_url = Faker("image_url")
    category = FuzzyChoice(choices=["Personal Care", "Home Decor", "Food", "Utensils"])
