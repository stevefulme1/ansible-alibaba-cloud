#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ram_group_policy_attachment_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ram_group_policy_attachment_info
short_description: Query ram group policy attachment resources.
description:
  - Retrieve information about Alibaba Cloud ram group policy attachment resources.
  - This is a read-only module that does not modify any resources.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  group_name:
    description: Filter by group name.
    type: str
  limit:
    description:
      - Maximum number of results to return.
    type: int
    default: 100
  offset:
    description:
      - Number of results to skip for pagination.
    type: int
    default: 0
"""

EXAMPLES = r"""
- name: List all ram group policy attachment resources
  stevefulme1.alibaba_cloud.ram_group_policy_attachment_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    group_name: example-value
"""

RETURN = r"""
ram_group_policy_attachments:
  description: List of ram group policy attachment resources.
  returned: success
  type: list
  elements: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        group_name=dict(type="str"),
        limit=dict(type="int", default=100),
        offset=dict(type="int", default=0),
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
    if module.params.get("group_name"):
        params["GroupName"] = module.params["group_name"]

    try:
        result = client.get(
            "ListPoliciesForGroup",
            params,
            service_endpoint="ram.aliyuncs.com",
            api_version="2015-05-01",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    data = result
    data = data.get("Policies", {})
    data = data.get("Policy", {})
    if not isinstance(data, list):
        data = [data] if data else []

    module.exit_json(changed=False, ram_group_policy_attachments=data)


if __name__ == "__main__":
    main()
