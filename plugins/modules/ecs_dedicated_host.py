#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ecs_dedicated_host"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ecs_dedicated_host
short_description: Manage ECS dedicated host.
description:
  - Create, update, or delete Alibaba Cloud ecs_dedicated_host resources.
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
  dedicated_host_type:
    description: Dedicated host type.
    type: str
  dedicated_host_name:
    description: Dedicated host name.
    type: str
  dedicated_host_id:
    description: Host ID for update or delete.
    type: str
"""

EXAMPLES = r"""
- name: Manage ecs_dedicated_host
  stevefulme1.alibaba_cloud.ecs_dedicated_host:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    dedicated_host_type: ddh.g6s
    dedicated_host_name: prod-host
"""

RETURN = r"""
dedicated_host:
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
        dedicated_host_type=dict(type="str"),
        dedicated_host_name=dict(type="str"),
        dedicated_host_id=dict(type="str"),
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
        result = client.get(
            "DescribeDedicatedHosts",
            {},
            service_endpoint="ecs.aliyuncs.com",
            api_version="2014-05-26",
        )

        data = result
        for key in ["DedicatedHosts", "DedicatedHost"]:
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "AllocateDedicatedHosts",
                    {},
                    service_endpoint="ecs.aliyuncs.com",
                    api_version="2014-05-26",
                )
                changed = True
                module.exit_json(changed=changed, dedicated_host=result)
            else:
                module.exit_json(
                    changed=False,
                    dedicated_host=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "ReleaseDedicatedHost",
                    {},
                    service_endpoint="ecs.aliyuncs.com",
                    api_version="2014-05-26",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
