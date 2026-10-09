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
Test cases for Product Model
"""

# pylint: disable=duplicate-code
import os
import logging
from decimal import Decimal
from unittest import TestCase
from wsgi import app
from service.models import Product, DataValidationError, db

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

    @staticmethod
    def make_product(**overrides):
        """Build an unsaved product with explicit, valid test data."""
        data = {
            "name": "Notebook",
            "description": "A paper notebook",
            "price": Decimal("19.99"),
        }
        data.update(overrides)
        return Product(**data)

    def test_create_and_retrieve_product(self):
        """It should persist all product fields and assign unique IDs"""
        product = self.make_product()
        product.create()
        product_id = product.id
        self.assertIsNotNone(product_id)
        other = self.make_product(name="Pencil")
        other.create()
        self.assertNotEqual(product_id, other.id)
        # Clear the identity map so retrieval must read from the database.
        db.session.remove()
        found = Product.find(product_id)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Notebook")
        self.assertEqual(found.description, "A paper notebook")
        self.assertEqual(found.price, Decimal("19.99"))

    def test_preserve_price_precision(self):
        """It should retrieve the exact price as a Decimal"""
        product = self.make_product()
        product.create()
        product_id = product.id
        db.session.remove()
        found = Product.find(product_id)
        self.assertIsInstance(found.price, Decimal)
        self.assertEqual(found.price, Decimal("19.99"))

    def test_update_product(self):
        """It should persist changed fields without changing the ID"""
        product = self.make_product()
        product.create()
        product_id = product.id
        product.name = "Updated notebook"
        product.description = "A larger notebook"
        product.price = Decimal("24.50")
        product.update()
        self.assertEqual(product.id, product_id)
        db.session.remove()
        found = Product.find(product_id)
        self.assertEqual(found.name, "Updated notebook")
        self.assertEqual(found.description, "A larger notebook")
        self.assertIsInstance(found.price, Decimal)
        self.assertEqual(found.price, Decimal("24.50"))
        self.assertEqual(len(Product.all()), 1)

    def test_delete_product(self):
        """It should remove a saved product from the database"""
        product = self.make_product()
        product.create()
        product_id = product.id
        product.delete()
        db.session.remove()
        self.assertIsNone(Product.find(product_id))
        self.assertEqual(Product.all(), [])

    def test_list_products(self):
        """It should return every saved product"""
        first = self.make_product()
        second = self.make_product(name="Pencil", price=Decimal("1.25"))
        first.create()
        second.create()
        expected_ids = {first.id, second.id}
        db.session.remove()
        products = Product.all()
        self.assertEqual(len(products), 2)
        self.assertEqual({product.id for product in products}, expected_ids)

    def test_list_empty_database(self):
        """It should return an empty list when no products exist"""
        self.assertEqual(Product.all(), [])

    def test_find_missing_product(self):
        """It should return None for an unknown ID"""
        self.assertIsNone(Product.find(999999))

    def test_reject_invalid_name(self):
        """It should reject missing, empty, and whitespace-only names"""
        for name in (None, "", "   ", "\t\n"):
            with self.subTest(name=name):
                product = self.make_product(name=name)
                with self.assertRaises(DataValidationError):
                    product.create()
                db.session.remove()
                self.assertEqual(Product.all(), [])

    def test_reject_invalid_price(self):
        """It should reject missing and negative prices without saving"""
        for price in (None, Decimal("-0.01")):
            with self.subTest(price=price):
                product = self.make_product(price=price)
                with self.assertRaises(DataValidationError):
                    product.create()
                db.session.remove()
                self.assertEqual(Product.all(), [])

    def test_reject_omitted_required_fields(self):
        """It should reject creation when a required field is omitted"""
        for field in ("name", "price"):
            with self.subTest(field=field):
                data = {"name": "Notebook", "description": "Paper", "price": Decimal("19.99")}
                del data[field]
                product = Product(**data)
                with self.assertRaises(DataValidationError):
                    product.create()
                db.session.remove()
                self.assertEqual(Product.all(), [])

    def test_allow_zero_price(self):
        """It should save a free product with a zero Decimal price"""
        product = self.make_product(price=Decimal("0.00"))
        product.create()
        product_id = product.id
        db.session.remove()
        found = Product.find(product_id)
        self.assertIsInstance(found.price, Decimal)
        self.assertEqual(found.price, Decimal("0.00"))

    def test_serialize_product(self):
        """It should serialize all fields without losing decimal precision"""
        product = self.make_product()
        product.create()
        data = product.serialize()
        self.assertIsInstance(data, dict)
        self.assertEqual(set(data), {"id", "name", "description", "price"})
        self.assertEqual(data["id"], product.id)
        self.assertEqual(data["name"], "Notebook")
        self.assertEqual(data["description"], "A paper notebook")
        # Both exact strings and Decimal values satisfy the story;
        # the team's JSON representation has not yet been finalized.
        self.assertIsInstance(data["price"], (str, Decimal))
        self.assertEqual(Decimal(data["price"]), Decimal("19.99"))

    def test_deserialize_product(self):
        """It should load supplied fields and represent price as Decimal"""
        data = {"name": "Notebook", "description": "A paper notebook", "price": Decimal("19.99")}
        product = Product()
        self.assertIs(product.deserialize(data), product)
        self.assertEqual(product.name, data["name"])
        self.assertEqual(product.description, data["description"])
        self.assertIsInstance(product.price, Decimal)
        self.assertEqual(product.price, Decimal("19.99"))

    def test_serialize_deserialize_round_trip(self):
        """It should preserve product fields through dictionary conversion"""
        original = self.make_product()
        restored = Product().deserialize(original.serialize())
        self.assertEqual(restored.name, original.name)
        self.assertEqual(restored.description, original.description)
        self.assertIsInstance(restored.price, Decimal)
        self.assertEqual(restored.price, original.price)
