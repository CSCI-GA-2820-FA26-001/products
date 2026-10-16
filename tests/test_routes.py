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
from decimal import Decimal
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Product
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/products"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
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

    ######################################################################
    #  C R E A T E   T E S T   C A S E S
    ######################################################################

    def test_create_product(self):
        """It should Create a new Product"""
        test_product = ProductFactory()
        logging.debug("Test Product: %s", test_product.serialize())
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check data is correct
        new_product = response.get_json()
        self.assertIsNotNone(new_product["id"])  # DB assigned an id
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(Decimal(new_product["price"]), test_product.price)

        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(Decimal(new_product["price"]), test_product.price)

    def test_create_product_no_data(self):
        """It should not Create a Product with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_bad_price(self):
        """It should not Create a Product with a negative price"""
        test_product = ProductFactory().serialize()
        test_product["price"] = "-5.00"
        response = self.client.post(BASE_URL, json=test_product)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
        """It should not Create a Product with no Content-Type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_wrong_content_type(self):
        """It should not Create a Product with the wrong Content-Type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    ######################################################################
    #  R E A D   T E S T   C A S E S
    ######################################################################

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

    ######################################################################
    #  U P D A T E   T E S T   C A S E S
    ######################################################################

    def test_update_product(self):
        """It should Update an existing Product"""
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # change and put back
        new_product = response.get_json()
        new_product["description"] = "updated description"
        new_product["price"] = "9.99"
        response = self.client.put(f"{BASE_URL}/{new_product['id']}", json=new_product)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated = response.get_json()
        self.assertEqual(updated["id"], new_product["id"])
        self.assertEqual(updated["description"], "updated description")
        self.assertEqual(Decimal(updated["price"]), Decimal("9.99"))

        found = Product.find(new_product["id"])
        self.assertEqual(found.description, "updated description")

    def test_update_product_not_found(self):
        """It should not Update a Product that doesn't exist"""
        test_product = ProductFactory()
        response = self.client.put(f"{BASE_URL}/0", json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product_bad_data(self):
        """It should not Update a Product with invalid data"""
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        product_id = response.get_json()["id"]
        response = self.client.put(
            f"{BASE_URL}/{product_id}", json={"name": "Soap", "price": "-1"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_wrong_content_type(self):
        """It should not Update a Product with the wrong Content-Type"""
        response = self.client.put(
            f"{BASE_URL}/1", data="hello", content_type="text/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    ######################################################################
    #  D E L E T E   T E S T   C A S E S
    ######################################################################

    def test_delete_product(self):
        """It should delete a product and return 204 with an empty body"""
        product = ProductFactory()
        product.create()
        product_id = product.id

        response = self.client.delete(f"{BASE_URL}/{product_id}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, b"")
        # Read from the database again instead of relying on cached objects.
        db.session.remove()
        self.assertIsNone(Product.find(product_id))
        self.assertEqual(Product.all(), [])

    def test_delete_product_preserves_other_products(self):
        """It should delete only the requested product"""
        target = ProductFactory()
        target.create()
        target_id = target.id
        other = ProductFactory()
        other.create()
        other_id = other.id
        expected = other.serialize()

        response = self.client.delete(f"{BASE_URL}/{target_id}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, b"")
        db.session.remove()
        self.assertIsNone(Product.find(target_id))
        remaining = Product.find(other_id)
        self.assertIsNotNone(remaining)
        self.assertEqual(remaining.serialize(), expected)
        self.assertEqual(len(Product.all()), 1)

    def test_delete_product_not_found(self):
        """It should return an empty 204 for an unknown ID without changing products"""
        first = ProductFactory()
        second = ProductFactory()
        first.create()
        second.create()
        expected = {product.id: product.serialize() for product in Product.all()}
        missing_id = max(expected) + 1
        self.assertIsNone(Product.find(missing_id))

        response = self.client.delete(f"{BASE_URL}/{missing_id}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, b"")
        db.session.remove()
        self.assertIsNone(Product.find(missing_id))
        self.assertEqual(
            {product.id: product.serialize() for product in Product.all()}, expected
        )

    def test_delete_product_twice(self):
        """It should return an empty 204 on both requests to delete the same product"""
        product = ProductFactory()
        product.create()
        product_id = product.id

        first_response = self.client.delete(f"{BASE_URL}/{product_id}")
        self.assertEqual(first_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(first_response.data, b"")
        db.session.remove()
        self.assertIsNone(Product.find(product_id))

        second_response = self.client.delete(f"{BASE_URL}/{product_id}")
        self.assertEqual(second_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(second_response.data, b"")
        db.session.remove()
        self.assertIsNone(Product.find(product_id))
        self.assertEqual(Product.all(), [])

    ######################################################################
    #  L I S T   T E S T   C A S E S
    ######################################################################

    def test_list_products(self):
        """It should return every product with its fields as JSON"""
        expected = []
        for _ in range(3):
            product = ProductFactory()
            product.create()
            expected.append(product.serialize())

        resp = self.client.get(BASE_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.headers["Content-Type"], "application/json")

        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertCountEqual(data, expected)

    def test_list_products_empty(self):
        """It should return an empty array when no products exist"""
        resp = self.client.get(BASE_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.headers["Content-Type"], "application/json")
        self.assertEqual(resp.get_json(), [])

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
