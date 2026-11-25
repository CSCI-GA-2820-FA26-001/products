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

from service.common import status
from service.models import DataValidationError
from service.routes import api

ERROR_LABELS = {
    status.HTTP_400_BAD_REQUEST: "Bad Request",
    status.HTTP_404_NOT_FOUND: "Not Found",
    status.HTTP_405_METHOD_NOT_ALLOWED: "Method not Allowed",
    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: "Unsupported media type",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
}


######################################################################
# Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """Return a JSON 400 for invalid product data."""
    return {"message": str(error)}, status.HTTP_400_BAD_REQUEST


def flask_http_error(error):
    """Return JSON for HTTP errors handled by Flask."""
    response = error.get_response()
    response.set_data(app.json.dumps({"message": error.description}))
    response.mimetype = "application/json"
    return response


def add_legacy_error_fields(response):
    """Preserve the existing fields on JSON error responses."""
    label = ERROR_LABELS.get(response.status_code)
    if label is None or not response.is_json:
        return response

    payload = response.get_json()
    if isinstance(payload, dict) and "message" in payload:
        payload.setdefault("status", response.status_code)
        payload.setdefault("error", label)
        response.set_data(app.json.dumps(payload))

    return response
