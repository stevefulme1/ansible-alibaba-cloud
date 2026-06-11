#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.redis_whitelist_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: redis_whitelist_info
short_description: Query Redis IP whitelist.
description:
  - Retrieve information about Alibaba Cloud Redis instance IP whitelist.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  instance_id:
    description: Redis instance ID.
    type: str
    required: true
"""

EXAMPLES = r"""
- name: Query Redis IP whitelist
  stevefulme1.alibaba_cloud.redis_whitelist_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: r-xxx
"""

RETURN = r"""
redis_whitelists:
  description: List of Redis IP whitelist groups.
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
        instance_id=dict(type="str", required=True),
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

    params = {
        "InstanceId": module.params["instance_id"],
    }

    try:
        result = client.get(
            "DescribeSecurityIps",
            params,
            service_endpoint="r-kvstore.aliyuncs.com",
            api_version="2015-01-01",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in ["SecurityIpGroups", "SecurityIpGroup"]:
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, redis_whitelists=data)


if __name__ == "__main__":
    main()
