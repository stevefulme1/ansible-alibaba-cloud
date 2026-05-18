# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""EDA event source: Alibaba Cloud ActionTrail audit events."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import asyncio
import datetime
import json
import urllib.parse
import hashlib
import hmac
import uuid

from ansible.module_utils.urls import open_url


DOCUMENTATION = r"""
---
name: alibaba_cloud_events
short_description: Poll Alibaba Cloud ActionTrail for audit events.
description:
  - Polls the ActionTrail LookupEvents API for audit events.
  - Emits events matching configured event types.
  - Supports instance lifecycle, security group, and IAM events.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  access_key_id:
    description: Alibaba Cloud access key ID.
    type: str
    required: true
  access_key_secret:
    description: Alibaba Cloud access key secret.
    type: str
    required: true
  region_id:
    description: Region to poll events from.
    type: str
    default: cn-hangzhou
  poll_interval:
    description: Seconds between polling cycles.
    type: int
    default: 30
  event_types:
    description: List of event types to emit.
    type: list
    elements: str
    default:
      - instance_created
      - instance_deleted
      - security_group_changed
      - iam_policy_changed
"""

EXAMPLES = r"""
- name: Watch for instance and security events
  hosts: localhost
  sources:
    - stevefulme1.alibaba_cloud.alibaba_cloud_events:
        access_key_id: "{{ lookup('env', 'ALIBABA_CLOUD_ACCESS_KEY_ID') }}"
        access_key_secret: "{{ lookup('env', 'ALIBABA_CLOUD_ACCESS_KEY_SECRET') }}"
        region_id: cn-hangzhou
        poll_interval: 60
        event_types:
          - instance_created
          - instance_deleted
          - security_group_changed
"""

# Map friendly event type names to ActionTrail event names.
EVENT_MAP = {
    "instance_created": ["RunInstances", "CreateInstance"],
    "instance_deleted": ["DeleteInstance", "DeleteInstances"],
    "security_group_changed": [
        "AuthorizeSecurityGroup",
        "RevokeSecurityGroup",
        "CreateSecurityGroup",
        "DeleteSecurityGroup",
        "ModifySecurityGroupAttribute",
    ],
    "iam_policy_changed": [
        "CreatePolicy",
        "DeletePolicy",
        "AttachPolicyToUser",
        "DetachPolicyFromUser",
        "AttachPolicyToRole",
        "DetachPolicyFromRole",
    ],
}


def _sign_request(params, access_key_secret, method="GET"):
    """Generate Alibaba Cloud v1 signature for API request."""
    sorted_params = sorted(params.items())
    query_string = urllib.parse.urlencode(sorted_params, quote_via=urllib.parse.quote)
    string_to_sign = "%s&%%2F&%s" % (
        method,
        urllib.parse.quote(query_string, safe=""),
    )
    h = hmac.new(
        (access_key_secret + "&").encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha1,
    )
    import base64

    return base64.b64encode(h.digest()).decode("utf-8")


def _call_actiontrail(access_key_id, access_key_secret, region_id, start_time, end_time):
    """Call ActionTrail LookupEvents API."""
    endpoint = "actiontrail.%s.aliyuncs.com" % region_id
    params = {
        "Action": "LookupEvents",
        "Version": "2020-07-06",
        "Format": "JSON",
        "AccessKeyId": access_key_id,
        "SignatureMethod": "HMAC-SHA1",
        "SignatureVersion": "1.0",
        "SignatureNonce": str(uuid.uuid4()),
        "Timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "StartTime": start_time,
        "EndTime": end_time,
    }

    params["Signature"] = _sign_request(params, access_key_secret)
    url = "https://%s/?%s" % (
        endpoint,
        urllib.parse.urlencode(params, quote_via=urllib.parse.quote),
    )

    try:
        resp = open_url(url, method="GET", timeout=30)
        body = resp.read().decode("utf-8")
        return json.loads(body)
    except Exception:
        return {"Events": []}


def _classify_event(event_name):
    """Map an ActionTrail event name to a friendly type."""
    for friendly, api_names in EVENT_MAP.items():
        if event_name in api_names:
            return friendly
    return None


async def main(queue, args):
    """Poll ActionTrail and emit matching events to the EDA queue."""
    access_key_id = args.get("access_key_id")
    access_key_secret = args.get("access_key_secret")
    region_id = args.get("region_id", "cn-hangzhou")
    poll_interval = int(args.get("poll_interval", 30))
    event_types = args.get("event_types", list(EVENT_MAP.keys()))

    # Build set of ActionTrail event names we care about.
    wanted_api_names = set()
    for et in event_types:
        wanted_api_names.update(EVENT_MAP.get(et, []))

    last_poll = datetime.datetime.utcnow() - datetime.timedelta(seconds=poll_interval)

    while True:
        now = datetime.datetime.utcnow()
        start_time = last_poll.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        result = await asyncio.get_event_loop().run_in_executor(
            None,
            _call_actiontrail,
            access_key_id,
            access_key_secret,
            region_id,
            start_time,
            end_time,
        )

        events = result.get("Events", [])
        if isinstance(events, str):
            try:
                events = json.loads(events)
            except (json.JSONDecodeError, TypeError):
                events = []

        for event in events:
            event_name = event.get("EventName", "")
            if event_name not in wanted_api_names:
                continue

            friendly_type = _classify_event(event_name)
            if friendly_type is None:
                continue

            await queue.put(
                {
                    "alibaba_cloud": {
                        "event_type": friendly_type,
                        "event_name": event_name,
                        "event_time": event.get("EventTime", ""),
                        "region_id": region_id,
                        "user_name": event.get("UserName", ""),
                        "source_ip": event.get("SourceIpAddress", ""),
                        "request_id": event.get("RequestId", ""),
                        "resource_type": event.get("ResourceType", ""),
                        "resource_name": event.get("ResourceName", ""),
                        "raw_event": event,
                    }
                }
            )

        last_poll = now
        await asyncio.sleep(poll_interval)


if __name__ == "__main__":
    """Entry point for standalone testing."""

    class MockQueue:
        """Simple mock queue for testing."""

        async def put(self, event):
            """Print event to stdout."""
            print(json.dumps(event, indent=2))

    asyncio.run(
        main(
            MockQueue(),
            {
                "access_key_id": "test",
                "access_key_secret": "test",
                "region_id": "cn-hangzhou",
                "poll_interval": 10,
            },
        )
    )
