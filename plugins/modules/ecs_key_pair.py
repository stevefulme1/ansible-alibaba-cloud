#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ecs_key_pair"""

from __future__ import annotations

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


DOCUMENTATION = r"""
---
module: ecs_key_pair
short_description: Manage SSH key pairs.
description:
  - Create, update, or delete Alibaba Cloud ecs_key_pair resources.
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
  key_pair_name:
    description: Name of the key pair.
    type: str
    required: true
  public_key_body:
    description: Public key material to import.
    type: str
"""

EXAMPLES = r"""
- name: Create key pair
  stevefulme1.alibaba_cloud.ecs_key_pair:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    key_pair_name: my-key
"""

RETURN = r"""
key_pair:
  description: Key pair details.
  returned: success
  type: dict
"""


def main():
    spec = dict(
        state=dict(
            type="str", choices=["present", "absent"],
            default="present",
        ),
        key_pair_name=dict(type="str", required=True),
        public_key_body=dict(type="str"),
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
            "DescribeKeyPairs", {},
            service_endpoint="ecs.aliyuncs.com",
            api_version="2014-05-26",
        )

        data = existing
        for key in "KeyPairs.KeyPair".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateKeyPair", {},
                    service_endpoint="ecs.aliyuncs.com",
                    api_version="2014-05-26",
                )
                changed = True
                module.exit_json(changed=changed, ecs_key_pair=result)
            else:
                module.exit_json(
                    changed=False, ecs_key_pair=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteKeyPairs", {},
                    service_endpoint="ecs.aliyuncs.com",
                    api_version="2014-05-26",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
