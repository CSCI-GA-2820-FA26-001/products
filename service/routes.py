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

from flask import jsonify, request, url_for, abort  # use url_for for read()
from flask import current_app as app  # Import Flask application
from service.models import Product
from service.common import status


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Describe the service and provide the product collection URL."""
    app.logger.info("Request for Products service information")
    return (
        jsonify(
            name="Products Service",
            version="1.0.0",
            products_url=url_for("list_products"),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


@app.route("/products", methods=["POST"])
def create_products():
    """Create a Product from the JSON in the request body"""
    app.logger.info("Request to Create a Product...")
    check_content_type("application/json")

    product = Product()
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product.deserialize(data)  # bad data -> DataValidationError -> 400
    product.create()
    app.logger.info("Product with new id [%s] saved!", product.id)

    location_url = url_for("get_products", product_id=product.id, _external=True)
    return (
        jsonify(product.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
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
# READ A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    """Retrieve a single Product"""
    app.logger.info("Request for product with id: %s", product_id)

    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product with id '{product_id}' was not found.",
        )

    app.logger.info("Returning product: %s", product.name)
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    """Update the Product with the given id from the JSON in the request body"""
    app.logger.info("Request to Update product with id [%s]", product_id)
    check_content_type("application/json")

    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found."
        )

    product.deserialize(request.get_json())
    product.id = product_id
    product.update()

    app.logger.info("Product with id [%s] updated.", product.id)
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    """Delete a product, returning no content even when it is absent."""
    app.logger.info("Request to delete product with id: %s", product_id)
    product = Product.find(product_id)
    if product is not None:
        product.delete()
        app.logger.info("Deleted product with id: %s", product_id)
    else:
        app.logger.info("Product with id %s is already absent", product_id)
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# LIST A PRODUCT
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """List products, optionally filtered by exact name and price range."""
    app.logger.info("Request for product list")

    products = Product.find_by_filters(
        name=request.args.get("name"),
        min_price=request.args.get("min_price"),
        max_price=request.args.get("max_price"),
    ).all()

    results = [product.serialize() for product in products]
    app.logger.info("Returning %d products", len(results))
    return jsonify(results), status.HTTP_200_OK
