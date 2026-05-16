#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ram_group"""

from __future__ import annotations


DOCUMENTATION = r"""
---
module: ram_group
short_description: Manage RAM groups.
description:
  - Create, update, or delete Alibaba Cloud ram_group resources.
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
    description: RAM group name.
    type: str
    required: true
"""

EXAMPLES = r"""
- name: Create RAM group
  stevefulme1.alibaba_cloud.ram_group:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    group_name: developers
"""

RETURN = r"""
group:
  description: RAM group details.
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
        group_name=dict(type="str", required=True),
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
        # Describe existing resources to check idempotency.
        existing = client.get(
            "ListGroups",
            {},
            service_endpoint="ram.aliyuncs.com",
            api_version="2015-05-01",
        )

        data = existing
        for key in "Groups.Group".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateGroup",
                    {},
                    service_endpoint="ram.aliyuncs.com",
                    api_version="2015-05-01",
                )
                changed = True
                module.exit_json(changed=changed, ram_group=result)
            else:
                module.exit_json(
                    changed=False,
                    ram_group=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteGroup",
                    {},
                    service_endpoint="ram.aliyuncs.com",
                    api_version="2015-05-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
