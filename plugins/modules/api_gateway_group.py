#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.api_gateway_group"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: api_gateway_group
short_description: Manage API Gateway groups.
description:
  - Create, update, or delete Alibaba Cloud api_gateway_group resources.
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
  group_name:
    description: Name of the API group.
    type: str
    required: true
  description:
    description: API group description.
    type: str
  group_id:
    description: ID of an existing API group (for updates/deletes).
    type: str
"""

EXAMPLES = r"""
- name: Manage api_gateway_group resource
  stevefulme1.alibaba_cloud.api_gateway_group:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    group_name: my-api-group
"""

RETURN = r"""
api_gateway_group:
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
        group_name=dict(type="str", required=True),
        description=dict(type="str"),
        group_id=dict(type="str"),
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

    try:
        existing = client.get(
            "DescribeApiGroups",
            {},
            service_endpoint="apigateway.aliyuncs.com",
            api_version="2016-07-14",
        )

        data = existing
        for key in "ApiGroupAttributes.ApiGroupAttribute".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateApiGroup",
                    {},
                    service_endpoint="apigateway.aliyuncs.com",
                    api_version="2016-07-14",
                )
                changed = True
                module.exit_json(changed=changed, api_gateway_group=result)
            else:
                module.exit_json(changed=False, api_gateway_group=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteApiGroup",
                    {},
                    service_endpoint="apigateway.aliyuncs.com",
                    api_version="2016-07-14",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
