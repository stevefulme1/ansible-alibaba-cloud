#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.eci_container_group"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: eci_container_group
short_description: Manage ECI container groups.
description:
  - Create or delete manage eci container groups.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  state:
    description: Desired state of the resource.
    type: str
    choices: ['present', 'absent']
    default: present
  container_group_id:
    description: Container group ID.
    type: str
  container_group_name:
    description: Container group name.
    type: str
  containers:
    description: List of container definitions.
    type: list
    elements: dict
  vswitch_id:
    description: VSwitch ID for the container group.
    type: str
  security_group_id:
    description: Security group ID.
    type: str"""

EXAMPLES = r"""
- name: Manage ECI container groups.
  stevefulme1.alibaba_cloud.eci_container_group:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
eci_container_group:
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
        container_group_id=dict(type="str"),
        container_group_name=dict(type="str"),
        containers=dict(type="list", elements="dict"),
        vswitch_id=dict(type="str"),
        security_group_id=dict(type="str"),
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
            "DescribeContainerGroups",
            {},
            service_endpoint="eci.aliyuncs.com",
            api_version="2018-08-08",
        )

        data = existing
        for key in "ContainerGroups".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateContainerGroup",
                    {},
                    service_endpoint="eci.aliyuncs.com",
                    api_version="2018-08-08",
                )
                changed = True
                module.exit_json(changed=changed, eci_container_group=result)
            else:
                module.exit_json(changed=False, eci_container_group=data[0])

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteContainerGroup",
                    {},
                    service_endpoint="eci.aliyuncs.com",
                    api_version="2018-08-08",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
