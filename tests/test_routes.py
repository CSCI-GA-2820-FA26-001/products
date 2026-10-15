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
TestProduct API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Product
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_product(self):
        """It should read a product and return its fields as JSON"""
        product = ProductFactory()
        product.create()

        resp = self.client.get(f"/products/{product.id}")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.headers["Content-Type"], "application/json")

        data = resp.get_json()
        self.assertEqual(data["id"], product.id)
        self.assertEqual(data["name"], product.name)
        self.assertEqual(data["description"], product.description)
        self.assertEqual(data["price"], str(product.price))

    def test_get_product_not_found(self):
        """It should return a JSON 404 when the product does not exist"""
        resp = self.client.get("/products/0")

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.headers["Content-Type"], "application/json")

        data = resp.get_json()
        self.assertEqual(data["status"], status.HTTP_404_NOT_FOUND)
        self.assertEqual(data["error"], "Not Found")
        self.assertIn(
            "Product with id '0' was not found.",
            data["message"],
        )
<<<<<<< Updated upstream
    
    def test_list_products(self):
        """It should list all products as a JSON array"""
=======

    def test_list_products(self):
        """It should return every product with its fields as JSON"""
>>>>>>> Stashed changes
        expected = []
        for _ in range(3):
            product = ProductFactory()
            product.create()
            expected.append(product.serialize())

<<<<<<< Updated upstream
        resp = self.client.get("/products")
=======
        resp = self.client.get(BASE_URL)
>>>>>>> Stashed changes

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.headers["Content-Type"], "application/json")

        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertCountEqual(data, expected)

    def test_list_products_empty(self):
<<<<<<< Updated upstream
        """It should return an empty JSON array when no products exist"""
        resp = self.client.get("/products")
=======
        """It should return an empty array when no products exist"""
        resp = self.client.get(BASE_URL)
>>>>>>> Stashed changes

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.headers["Content-Type"], "application/json")
        self.assertEqual(resp.get_json(), [])

<<<<<<< Updated upstream
=======
    def test_list_products_by_name(self):
        """It should return all products with the exact requested name"""
        expected = []

        for name in ["Notebook", "Notebook", "Notebook Stand"]:
            product = ProductFactory(name=name)
            product.create()
            if name == "Notebook":
                expected.append(product.serialize())

        resp = self.client.get(
            BASE_URL,
            query_string={"name": "Notebook"},
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.headers["Content-Type"], "application/json")

        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertCountEqual(data, expected)

    def test_list_products_by_name_not_found(self):
        """It should return an empty array when no product name matches"""
        product = ProductFactory(name="Pencil")
        product.create()

        resp = self.client.get(
            BASE_URL,
            query_string={"name": "Notebook"},
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.headers["Content-Type"], "application/json")
        self.assertEqual(resp.get_json(), [])
>>>>>>> Stashed changes
