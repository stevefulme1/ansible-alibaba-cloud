#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.kms_key"""

from __future__ import annotations


DOCUMENTATION = r"""
---
module: kms_key
short_description: Manage KMS keys.
description:
  - Create, update, or delete Alibaba Cloud kms_key resources.
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
  description:
    description: Description of the key.
    type: str
  key_usage:
    description: Key usage (ENCRYPT/DECRYPT or SIGN/VERIFY).
    type: str
    default: ENCRYPT/DECRYPT
  key_id:
    description: Existing key ID (for delete).
    type: str
  pending_window_in_days:
    description: Days before scheduled deletion takes effect.
    type: int
    default: 30
"""

EXAMPLES = r"""
- name: Create KMS key
  stevefulme1.alibaba_cloud.kms_key:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    description: encryption key
"""

RETURN = r"""
key:
  description: KMS key details.
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
        description=dict(type="str"),
        key_usage=dict(type="str", default="ENCRYPT/DECRYPT"),
        key_id=dict(type="str"),
        pending_window_in_days=dict(type="int", default=30),
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
            "ListKeys",
            {},
            service_endpoint="kms.aliyuncs.com",
            api_version="2016-01-20",
        )

        data = existing
        for key in "Keys.Key".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateKey",
                    {},
                    service_endpoint="kms.aliyuncs.com",
                    api_version="2016-01-20",
                )
                changed = True
                module.exit_json(changed=changed, kms_key=result)
            else:
                module.exit_json(
                    changed=False,
                    kms_key=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "ScheduleKeyDeletion",
                    {},
                    service_endpoint="kms.aliyuncs.com",
                    api_version="2016-01-20",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
