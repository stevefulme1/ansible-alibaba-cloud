#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.redis_whitelist"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: redis_whitelist
short_description: Manage Redis IP whitelist.
description:
  - Create, update, or delete Alibaba Cloud redis_whitelist resources.
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
  instance_id:
    description: Redis instance ID.
    type: str
  security_ip_group_name:
    description: Whitelist group name.
    type: str
  security_ips:
    description: Comma-separated IP addresses.
    type: str
"""

EXAMPLES = r"""
- name: Manage redis_whitelist
  stevefulme1.alibaba_cloud.redis_whitelist:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    instance_id: r-xxx
    security_ips: 10.0.0.0/8
"""

RETURN = r"""
redis_whitelist:
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
        state=dict(
            type="str",
            choices=["present", "absent"],
            default="present",
        ),
        instance_id=dict(type="str"),
        security_ip_group_name=dict(type="str"),
        security_ips=dict(type="str"),
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
    if module.params.get("instance_id") is not None:
        params["InstanceId"] = module.params["instance_id"]
    if module.params.get("security_ip_group_name") is not None:
        params["SecurityIpGroupName"] = module.params["security_ip_group_name"]
    if module.params.get("security_ips") is not None:
        params["SecurityIps"] = module.params["security_ips"]


    try:
        result = client.get(
            "DescribeSecurityIps",
            params,
            service_endpoint="r-kvstore.aliyuncs.com",
            api_version="2015-01-01",
        )

        data = result
        for key in ["SecurityIpGroups", "SecurityIpGroup"]:
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "ModifySecurityIps",
                    params,
                    service_endpoint="r-kvstore.aliyuncs.com",
                    api_version="2015-01-01",
                )
                changed = True
                module.exit_json(changed=changed, redis_whitelist=result)
            else:
                module.exit_json(
                    changed=False,
                    redis_whitelist=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "ModifySecurityIps",
                    params,
                    service_endpoint="r-kvstore.aliyuncs.com",
                    api_version="2015-01-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
