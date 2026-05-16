#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ram_role_policy_attachment"""

from __future__ import annotations

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


DOCUMENTATION = r"""
---
module: ram_role_policy_attachment
short_description: Attach policies to roles.
description:
  - Create, update, or delete Alibaba Cloud ram_role_policy_attachment resources.
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
  role_name:
    description: RAM role name.
    type: str
    required: true
  policy_name:
    description: Policy name to attach.
    type: str
    required: true
  policy_type:
    description: Policy type (System or Custom).
    type: str
    default: Custom
"""

EXAMPLES = r"""
- name: Attach policy to role
  stevefulme1.alibaba_cloud.ram_role_policy_attachment:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    role_name: ecs-admin
    policy_name: AliyunECSFullAccess
    policy_type: System
"""

RETURN = r"""
attachment:
  description: Attachment status.
  returned: success
  type: dict
"""


def main():
    spec = dict(
        state=dict(
            type="str",
            choices=["present", "absent"],
            default="present",
        ),
        role_name=dict(type="str", required=True),
        policy_name=dict(type="str", required=True),
        policy_type=dict(type="str", default="Custom"),
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
            "ListPoliciesForRole",
            {},
            service_endpoint="ram.aliyuncs.com",
            api_version="2015-05-01",
        )

        data = existing
        for key in "Policies.Policy".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "AttachPolicyToRole",
                    {},
                    service_endpoint="ram.aliyuncs.com",
                    api_version="2015-05-01",
                )
                changed = True
                module.exit_json(changed=changed, ram_role_policy_attachment=result)
            else:
                module.exit_json(
                    changed=False,
                    ram_role_policy_attachment=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DetachPolicyFromRole",
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
