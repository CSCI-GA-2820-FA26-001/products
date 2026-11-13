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

    def test_health(self):
        """It should return a healthy status as JSON"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.get_json(), {"status": "OK"})

    def test_index(self):
        """It should serve the shared administration UI without changing products."""
        product = ProductFactory()
        product.create()
        original = product.serialize()

        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.mimetype, "text/html")
        html = response.get_data(as_text=True)
        self.assertIn("<title>Products Administration</title>", html)
        self.assertIn('id="product_name"', html)
        self.assertIn('id="search_results"', html)
        self.assertIn('id="feedback_results"', html)
        self.assertEqual(Product.find(product.id).serialize(), original)

    def test_ui_assets(self):
        """It should serve the local CSS and JavaScript needed by the UI."""
        for path in (
            "/static/css/cerulean_bootstrap.min.css",
            "/static/js/jquery-3.6.0.min.js",
            "/static/js/rest_api.js",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

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

    def test_query_products(self):
        """It should return exactly the products matching all filters."""
        records = [
            ("Notebook", "0"),
            ("Notebook", "10"),
            ("Notebook", "20"),
            ("Notebook", "30"),
            ("Notebook Stand", "15"),
            ("Pencil", "20.01"),
        ]
        products = []
        for name, price in records:
            product = ProductFactory(name=name, price=Decimal(price))
            product.create()
            products.append(product)

        cases = [
            ({}, [0, 1, 2, 3, 4, 5]),
            ({"name": "Notebook"}, [0, 1, 2, 3]),
            ({"min_price": "20"}, [2, 3, 5]),
            ({"max_price": "20"}, [0, 1, 2, 4]),
            ({"min_price": "10", "max_price": "20"}, [1, 2, 4]),
            ({"name": "Notebook", "min_price": "10", "max_price": "20"}, [1, 2]),
            ({"name": "Notebook", "min_price": "20"}, [2, 3]),
            ({"name": "Notebook", "max_price": "10"}, [0, 1]),
            ({"min_price": "20.01", "max_price": "20.01"}, [5]),
            ({"min_price": "0", "max_price": "0"}, [0]),
            ({"name": "Missing"}, []),
            ({"min_price": "100"}, []),
            ({"name": "Pencil", "max_price": "20"}, []),
        ]
        for filters, expected_indexes in cases:
            with self.subTest(filters=filters):
                response = self.client.get(BASE_URL, query_string=filters)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.mimetype, "application/json")
                self.assertCountEqual(
                    response.get_json(),
                    [products[index].serialize() for index in expected_indexes],
                )

    def test_query_products_invalid_prices(self):
        """It should return a JSON 400 error for invalid price filters."""
        invalid_values = (
            "",
            " ",
            "abc",
            "true",
            "-0.01",
            "NaN",
            "sNaN",
            "Infinity",
            "-Infinity",
        )
        for field in ("min_price", "max_price"):
            for value in invalid_values:
                with self.subTest(field=field, value=value):
                    response = self.client.get(BASE_URL, query_string={field: value})
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                    self.assertEqual(response.mimetype, "application/json")
                    data = response.get_json()
                    self.assertEqual(data["status"], status.HTTP_400_BAD_REQUEST)
                    self.assertEqual(data["error"], "Bad Request")
                    self.assertIn(field, data["message"])

    def test_query_products_invalid_range(self):
        """It should return a JSON 400 error for a reversed price range."""
        response = self.client.get(
            BASE_URL, query_string={"min_price": "30", "max_price": "10"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIn("min_price", response.get_json()["message"])

    def test_query_products_empty_catalog(self):
        """It should return an empty JSON array for an empty catalog."""
        response = self.client.get(
            BASE_URL, query_string={"min_price": "10", "max_price": "20"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.get_json(), [])

    ######################################################################
    #  R E V I E W   A C T I O N   T E S T   C A S E S
    ######################################################################

    VALID_REVIEW = {"rating": 5, "text": "Good quality and worth the price."}

    def _create_product(self):
        """Helper: POST a product and return its JSON"""
        response = self.client.post(BASE_URL, json=ProductFactory().serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.get_json()

    def _review_url(self, product_id):
        """Helper: the review endpoint for a product"""
        return f"{BASE_URL}/{product_id}/comments"

    def test_review_product(self):
        """It should add a rating and review to a Product"""
        product = self._create_product()
        self.assertEqual(product["reviews"], [])  # Given no reviews

        response = self.client.post(
            self._review_url(product["id"]), json=self.VALID_REVIEW
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data["reviews"]), 1)
        self.assertEqual(data["reviews"][0]["rating"], 5)
        self.assertEqual(data["reviews"][0]["text"], self.VALID_REVIEW["text"])

        # retrieving the product again shows the saved review
        saved = self.client.get(f"{BASE_URL}/{product['id']}").get_json()
        self.assertEqual(saved["reviews"], data["reviews"])

    def test_review_preserves_previous_reviews(self):
        """It should keep earlier reviews when a new one is added"""
        product = self._create_product()
        url = self._review_url(product["id"])
        self.client.post(url, json={"rating": 4, "text": "First"})
        response = self.client.post(url, json={"rating": 2, "text": "Second"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        texts = [review["text"] for review in response.get_json()["reviews"]]
        self.assertEqual(texts, ["First", "Second"])  # both kept, in order

    def test_review_rating_boundaries(self):
        """It should accept ratings of 1 and 5"""
        for rating in (1, 5):
            with self.subTest(rating=rating):
                product = self._create_product()
                response = self.client.post(
                    self._review_url(product["id"]),
                    json={"rating": rating, "text": "Review"},
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.get_json()["reviews"][0]["rating"], rating)

    def test_review_invalid_payloads(self):
        """It should reject invalid reviews and leave the Product unchanged"""
        invalid_payloads = [
            {"rating": 0, "text": "Review"},
            {"rating": 6, "text": "Review"},
            {"rating": 4.5, "text": "Review"},
            {"rating": "5", "text": "Review"},
            {"rating": True, "text": "Review"},
            {"text": "Review"},
        ]
        product = self._create_product()
        url = self._review_url(product["id"])
        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.post(url, json=payload)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("message", response.get_json())  # JSON error body

        saved = self.client.get(f"{BASE_URL}/{product['id']}").get_json()
        self.assertEqual(saved["reviews"], [])  # nothing was saved

    def test_review_product_not_found(self):
        """It should return 404 when reviewing a Product that doesn't exist"""
        response = self.client.post(self._review_url(0), json=self.VALID_REVIEW)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("message", response.get_json())

    def test_review_wrong_content_type(self):
        """It should not accept a review that isn't JSON"""
        product = self._create_product()
        response = self.client.post(
            self._review_url(product["id"]), data="hello", content_type="text/plain"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_review_body_not_an_object(self):
        """It should reject a JSON body that isn't an object"""
        product = self._create_product()
        response = self.client.post(self._review_url(product["id"]), json=[5, "Review"])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
