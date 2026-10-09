"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Product


class ProductFactory(factory.Factory):
    """Creates fake products for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Product

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"Product {n}")

    description = factory.Faker("sentence")
    price = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
