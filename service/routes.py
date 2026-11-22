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
Product Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Product
"""

from flask import abort, jsonify, request
from flask import current_app as app
from flask_restx import Api, Resource

from service.common import status
from service.models import Product

api = Api(prefix="/api", doc="/apidocs/")


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Serve the shared Products administration page."""
    return app.send_static_file("index.html")


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health", methods=["GET"])
def health():
    """Return the service health status for Kubernetes probes."""
    return jsonify(status="OK"), status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


@api.route("/products")
class ProductCollection(Resource):
    """List and create products."""

    def get(self):
        """List products, optionally filtered by exact name and price range."""
        app.logger.info("Request for product list")
        products = Product.find_by_filters(
            name=request.args.get("name"),
            min_price=request.args.get("min_price"),
            max_price=request.args.get("max_price"),
        ).all()

        results = [product.serialize() for product in products]
        app.logger.info("Returning %d products", len(results))
        return results, status.HTTP_200_OK

    def post(self):
        """Create a product from the JSON request body."""
        app.logger.info("Request to Create a Product...")
        check_content_type("application/json")

        product = Product()
        data = request.get_json()
        app.logger.info("Processing: %s", data)
        product.deserialize(data)
        product.create()
        app.logger.info("Product with new id [%s] saved!", product.id)

        location_url = api.url_for(
            ProductResource, product_id=product.id, _external=True
        )
        return product.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct."""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )
    if request.headers["Content-Type"] != content_type:
        app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )


######################################################################
# READ / UPDATE / DELETE A PRODUCT
######################################################################
@api.route("/products/<int:product_id>")
class ProductResource(Resource):
    """Read, update, and delete a single product."""

    def get(self, product_id):
        """Retrieve a single product."""
        app.logger.info("Request for product with id: %s", product_id)
        product = Product.find(product_id)
        if not product:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' was not found.",
            )

        app.logger.info("Returning product: %s", product.name)
        return product.serialize(), status.HTTP_200_OK

    def put(self, product_id):
        """Update a product from the JSON request body."""
        app.logger.info("Request to Update product with id [%s]", product_id)
        check_content_type("application/json")

        product = Product.find(product_id)
        if not product:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' was not found.",
            )

        product.deserialize(request.get_json())
        product.id = product_id
        product.update()
        app.logger.info("Product with id [%s] updated.", product.id)
        return product.serialize(), status.HTTP_200_OK

    def delete(self, product_id):
        """Delete a product and return no content even if it is absent."""
        app.logger.info("Request to delete product with id: %s", product_id)
        product = Product.find(product_id)
        if product is not None:
            product.delete()
            app.logger.info("Deleted product with id: %s", product_id)
        else:
            app.logger.info("Product with id %s is already absent", product_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
# REVIEW A PRODUCT
######################################################################
@api.route("/products/<int:product_id>/comments")
class ProductReviews(Resource):
    """Handle reviews for a product."""

    def post(self, product_id):
        """Add a rating and written review to a product."""
        app.logger.info("Request to review product with id [%s]", product_id)
        check_content_type("application/json")

        product = Product.find(product_id)
        if not product:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' was not found.",
            )

        data = request.get_json()
        if not isinstance(data, dict):
            abort(status.HTTP_400_BAD_REQUEST, "Request body must be a JSON object")

        product.add_review(data.get("rating"), data.get("text", ""))
        app.logger.info("Review added to product with id [%s]", product_id)
        return product.serialize(), status.HTTP_200_OK
