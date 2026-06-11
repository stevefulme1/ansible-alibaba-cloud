#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.resource_manager_resource_group_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: resource_manager_resource_group_info
short_description: Query Resource Manager resource groups.
description:
  - Retrieve information about Alibaba Cloud Resource Manager resource groups.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  resource_group_id:
    description: Filter by resource group ID.
    type: str
  resource_group_name:
    description: Filter by resource group name.
    type: str
"""

EXAMPLES = r"""
- name: Query all resource groups
  stevefulme1.alibaba_cloud.resource_manager_resource_group_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific resource group
  stevefulme1.alibaba_cloud.resource_manager_resource_group_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    resource_group_id: rg-xxxxx
"""

RETURN = r"""
resource_manager_resource_groups:
  description: List of Resource Manager resource groups.
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
        resource_group_id=dict(type="str"),
        resource_group_name=dict(type="str"),
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
    if module.params.get("resource_group_id"):
        params["ResourceGroupId"] = module.params["resource_group_id"]
    if module.params.get("resource_group_name"):
        params["ResourceGroupName"] = module.params["resource_group_name"]

    try:
        result = client.get(
            "DescribeResourceGroup",
            params,
            service_endpoint="resourcemanager.aliyuncs.com",
            api_version="2020-03-31",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "ResourceGroups.ResourceGroup".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, resource_manager_resource_groups=data)


if __name__ == "__main__":
    main()
