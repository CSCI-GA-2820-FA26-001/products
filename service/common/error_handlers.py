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
Module: error_handlers
"""

from flask import current_app as app
from werkzeug.exceptions import (
    BadRequest,
    InternalServerError,
    MethodNotAllowed,
    NotFound,
    UnsupportedMediaType,
)

from service.common import status
from service.models import DataValidationError
from service.routes import api


######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """Handles Value Errors from bad data"""
    return bad_request(error)


@app.errorhandler(status.HTTP_400_BAD_REQUEST)
@api.errorhandler(BadRequest)
def bad_request(error):
    """Handles bad requests with 400_BAD_REQUEST"""
    message = str(error)
    app.logger.warning(message)
    code = status.HTTP_400_BAD_REQUEST
    return {"status": code, "error": "Bad Request", "message": message}, code


@app.errorhandler(status.HTTP_404_NOT_FOUND)
@api.errorhandler(NotFound)
def not_found(error):
    """Handles resources not found with 404_NOT_FOUND"""
    message = str(error)
    app.logger.warning(message)
    code = status.HTTP_404_NOT_FOUND
    return {"status": code, "error": "Not Found", "message": message}, code


@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
@api.errorhandler(MethodNotAllowed)
def method_not_supported(error):
    """Handles unsupported HTTP methods with 405_METHOD_NOT_SUPPORTED"""
    message = str(error)
    app.logger.warning(message)
    code = status.HTTP_405_METHOD_NOT_ALLOWED
    return {"status": code, "error": "Bad Request", "message": message}, code


@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
@api.errorhandler(UnsupportedMediaType)
def mediatype_not_supported(error):
    """Handles unsupported media requests with 415_UNSUPPORTED_MEDIA_TYPE"""
    message = str(error)
    app.logger.warning(message)
    code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    return {"status": code, "error": "Bad Request", "message": message}, code


@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
@api.errorhandler(InternalServerError)
def internal_server_error(error):
    """Handles unexpected server error with 500_SERVER_ERROR"""
    message = str(error)
    app.logger.error(message)
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return {"status": code, "error": "Bad Request", "message": message}, code


@api.errorhandler
def unexpected_api_error(_error):
    """Return the standard JSON 500 response for unexpected API errors."""
    return internal_server_error(InternalServerError())
