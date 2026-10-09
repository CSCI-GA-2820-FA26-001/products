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
    name = factory.Faker("first_name")

    # Todo: Add your other attributes here...
