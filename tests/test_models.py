######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from decimal import Decimal
from service.models import Product, DataValidationError, db   # test_models.py
from .factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Product   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProduct(TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should create a Product"""
        product = Product(name="Hat", description="A red hat", price=Decimal("12.50"))
        self.assertIsNone(product.id)                # not saved yet
        self.assertEqual(product.name, "Hat")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.price, Decimal("12.50"))

    def test_add_a_product(self):
        """It should add a Product to the database"""
        self.assertEqual(Product.all(), [])          # Given no products
        product = ProductFactory()
        product.create()                             # When I add a product
        self.assertIsNotNone(product.id)             # DB assigned an id
        products = Product.all()
        self.assertEqual(len(products), 1)           # Then there is 1 product
        found = Product.find(product.id)
        self.assertEqual(found.name, product.name)
        self.assertEqual(found.price, product.price)
    
    def test_repr(self):
        """It should return a readable representation"""
        product = ProductFactory()
        self.assertIn(product.name, repr(product))

    def test_serialize_a_product(self):
        """It should serialize a Product into a dictionary"""
        product = ProductFactory()
        data = product.serialize()
        self.assertEqual(data["id"], product.id)
        self.assertEqual(data["name"], product.name)
        self.assertEqual(data["description"], product.description)
        self.assertEqual(Decimal(str(data["price"])), product.price)  # works if price is str or Decimal
        
    def test_deserialize_a_product(self):
        """It should deserialize a Product from a dictionary"""
        data = ProductFactory().serialize()
        product = Product().deserialize(data)        # returns self
        self.assertEqual(product.name, data["name"])
        self.assertEqual(product.description, data["description"])
        self.assertEqual(product.price, Decimal(str(data["price"])))

    # ---------- sad paths ----------
    def test_deserialize_missing_data(self):
        """It should not deserialize a Product with missing fields"""
        self.assertRaises(DataValidationError, Product().deserialize, {"name": "Hat"})

    def test_deserialize_bad_data(self):
        """It should not deserialize something that isn't a dict"""
        self.assertRaises(DataValidationError, Product().deserialize, "not a dict")

    def test_deserialize_blank_name(self):
        """It should not deserialize a blank name"""
        data = ProductFactory().serialize()
        data["name"] = "   "
        self.assertRaises(DataValidationError, Product().deserialize, data)

    def test_deserialize_negative_price(self):
        """It should not deserialize a negative price"""
        data = ProductFactory().serialize()
        data["price"] = "-1.00"
        self.assertRaises(DataValidationError, Product().deserialize, data)

    def test_deserialize_non_numeric_price(self):
        """It should not deserialize a non-numeric price"""
        data = ProductFactory().serialize()
        data["price"] = "ten dollars"
        self.assertRaises(DataValidationError, Product().deserialize, data)
    # Todo: Add your test cases here...
