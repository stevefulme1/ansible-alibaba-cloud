#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.api_gateway_api_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: api_gateway_api_info
short_description: Query API Gateway APIs.
description:
  - Retrieve information about Alibaba Cloud API Gateway APIs.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  group_id:
    description: Filter by API group ID.
    type: str
  api_id:
    description: Filter by API ID.
    type: str
  api_name:
    description: Filter by API name.
    type: str
"""

EXAMPLES = r"""
- name: Query all API Gateway APIs
  stevefulme1.alibaba_cloud.api_gateway_api_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query APIs in a specific group
  stevefulme1.alibaba_cloud.api_gateway_api_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    group_id: grp-xxxxx
"""

RETURN = r"""
api_gateway_apis:
  description: List of API Gateway APIs.
  returned: success
  type: list
  elements: dict
  sample:
    - api_id: api-123
      api_name: GetUsers
      group_id: grp-xxxxx
      visibility: PUBLIC
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        group_id=dict(type="str"),
        api_id=dict(type="str"),
        api_name=dict(type="str"),
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

    params = {}
    if module.params.get("group_id"):
        params["GroupId"] = module.params["group_id"]
    if module.params.get("api_id"):
        params["ApiId"] = module.params["api_id"]
    if module.params.get("api_name"):
        params["ApiName"] = module.params["api_name"]

    try:
        result = client.get(
            "DescribeApis",
            params,
            service_endpoint="apigateway.aliyuncs.com",
            api_version="2016-07-14",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "ApiSummarys.ApiSummary".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, api_gateway_apis=data)


if __name__ == "__main__":
    main()
