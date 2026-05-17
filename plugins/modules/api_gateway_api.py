#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.api_gateway_api"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: api_gateway_api
short_description: Manage API Gateway API definitions.
description:
  - Create, update, or delete Alibaba Cloud api_gateway_api resources.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  state:
    description: Desired state of the resource.
    type: str
    choices: [present, absent]
    default: present
  group_id:
    description: API group ID for the API.
    type: str
    required: true
  api_name:
    description: Name of the API definition.
    type: str
    required: true
  api_id:
    description: ID of an existing API (for updates/deletes).
    type: str
  visibility:
    description: API visibility.
    type: str
    choices: [PUBLIC, PRIVATE]
    default: PUBLIC
  request_config:
    description: Request configuration.
    type: dict
  service_config:
    description: Service backend configuration.
    type: dict
"""

EXAMPLES = r"""
- name: Manage api_gateway_api resource
  stevefulme1.alibaba_cloud.api_gateway_api:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    group_id: grp-xxxxx
    api_name: GetUsers
    visibility: PUBLIC
"""

RETURN = r"""
api_gateway_api:
  description: Resource details.
  returned: success
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        state=dict(type="str", choices=["present", "absent"], default="present"),
        group_id=dict(type="str", required=True),
        api_name=dict(type="str", required=True),
        api_id=dict(type="str"),
        visibility=dict(type="str", choices=["PUBLIC", "PRIVATE"], default="PUBLIC"),
        request_config=dict(type="dict"),
        service_config=dict(type="dict"),
    )
    spec.update(alibaba_argument_spec)

    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True,
    )

    client = AlibabaCloudClient(
        access_key_id=module.params["access_key_id"],
        access_key_secret=module.params["access_key_secret"],
        region_id=module.params["region_id"],
        security_token=module.params.get("security_token"),
        timeout=module.params["timeout"],
    )

    state = module.params["state"]
    changed = False

    params = {}
    if module.params.get("group_id") is not None:
        params["GroupId"] = module.params["group_id"]
    if module.params.get("api_name") is not None:
        params["ApiName"] = module.params["api_name"]
    if module.params.get("api_id") is not None:
        params["ApiId"] = module.params["api_id"]
    if module.params.get("visibility") is not None:
        params["Visibility"] = module.params["visibility"]
    if module.params.get("request_config") is not None:
        params["RequestConfig"] = module.params["request_config"]
    if module.params.get("service_config") is not None:
        params["ServiceConfig"] = module.params["service_config"]

    try:
        existing = client.get(
            "DescribeApis",
            params,
            service_endpoint="apigateway.aliyuncs.com",
            api_version="2016-07-14",
        )

        data = existing
        for key in "ApiSummarys.ApiSummary".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateApi",
                    params,
                    service_endpoint="apigateway.aliyuncs.com",
                    api_version="2016-07-14",
                )
                changed = True
                module.exit_json(changed=changed, api_gateway_api=result)
            else:
                module.exit_json(changed=False, api_gateway_api=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteApi",
                    params,
                    service_endpoint="apigateway.aliyuncs.com",
                    api_version="2016-07-14",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
