# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Alibaba Cloud shared module utilities."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import datetime
import hashlib
import hmac
import json
import urllib.parse
import uuid

from ansible.module_utils.urls import open_url


class AlibabaCloudError(Exception):
    """Custom exception for Alibaba Cloud API errors."""

    def __init__(self, message, code=None, request_id=None):
        super().__init__(message)
        self.code = code
        self.request_id = request_id


# Common argument spec shared by every module.
alibaba_argument_spec = dict(
    access_key_id=dict(type="str", required=True),
    access_key_secret=dict(type="str", required=True, no_log=True),
    region_id=dict(type="str", required=True),
    security_token=dict(type="str", no_log=True),
    timeout=dict(type="int", default=60),
)


class AlibabaCloudClient:
    """Low-level REST client with HMAC-SHA256 request signing."""

    API_VERSION = "2014-05-26"  # default; callers override per-service

    def __init__(
        self,
        access_key_id,
        access_key_secret,
        region_id,
        security_token=None,
        timeout=60,
    ):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.region_id = region_id
        self.security_token = security_token
        self.timeout = timeout

    # ------------------------------------------------------------------ #
    #  Signing helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _percent_encode(value):
        """RFC 3986 percent-encoding."""
        return urllib.parse.quote(str(value), safe="")

    def _sign(self, params):
        """Compute SignatureVersion=1.0 HMAC-SHA256 signature."""
        sorted_params = sorted(params.items())
        query = "&".join(f"{self._percent_encode(k)}={self._percent_encode(v)}" for k, v in sorted_params)
        string_to_sign = f"GET&%2F&{self._percent_encode(query)}"
        key = f"{self.access_key_secret}&".encode("utf-8")
        digest = hmac.new(key, string_to_sign.encode("utf-8"), hashlib.sha256).digest()
        import base64

        return base64.b64encode(digest).decode("utf-8")

    # ------------------------------------------------------------------ #
    #  Core request method
    # ------------------------------------------------------------------ #

    def request(self, action, params=None, service_endpoint=None, api_version=None):
        """Send a signed request to the Alibaba Cloud API.

        Args:
            action: API action name (e.g. ``DescribeInstances``).
            params: Extra query parameters for the action.
            service_endpoint: Full hostname, e.g. ``ecs.aliyuncs.com``.
            api_version: Override the default API version string.

        Returns:
            Parsed JSON response as a dict.

        Raises:
            AlibabaCloudError: On HTTP or API-level errors.
        """
        if params is None:
            params = {}

        common = {
            "Action": action,
            "Format": "JSON",
            "Version": api_version or self.API_VERSION,
            "AccessKeyId": self.access_key_id,
            "SignatureMethod": "HMAC-SHA256",
            "Timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "SignatureVersion": "1.0",
            "SignatureNonce": str(uuid.uuid4()),
            "RegionId": self.region_id,
        }
        if self.security_token:
            common["SecurityToken"] = self.security_token

        merged = {**common, **params}
        merged["Signature"] = self._sign(merged)

        if service_endpoint is None:
            service_endpoint = "ecs.aliyuncs.com"

        query_string = urllib.parse.urlencode(merged)
        url = f"https://{service_endpoint}/?{query_string}"

        try:
            resp = open_url(url, method="GET", timeout=self.timeout)
            body = resp.read().decode("utf-8")
            return json.loads(body)
        except Exception as exc:
            raise AlibabaCloudError(f"API request failed: {exc}") from exc

    # ------------------------------------------------------------------ #
    #  Convenience HTTP verbs (all delegate to request)
    # ------------------------------------------------------------------ #

    def get(self, action, params=None, **kwargs):
        """Alias for ``request`` (GET is the default verb)."""
        return self.request(action, params, **kwargs)

    def post(self, action, params=None, **kwargs):
        """Alias kept for interface symmetry; Alibaba APIs use GET."""
        return self.request(action, params, **kwargs)

    def put(self, action, params=None, **kwargs):
        """Alias kept for interface symmetry."""
        return self.request(action, params, **kwargs)

    def delete(self, action, params=None, **kwargs):
        """Alias kept for interface symmetry."""
        return self.request(action, params, **kwargs)
