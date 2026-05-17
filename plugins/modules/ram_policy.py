#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ram_policy"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ram_policy
short_description: Manage RAM policies.
description:
  - Create, update, or delete Alibaba Cloud ram_policy resources.
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
  policy_name:
    description: RAM policy name.
    type: str
    required: true
  policy_document:
    description: Policy document as JSON string.
    type: str
  policy_type:
    description: Policy type.
    type: str
    default: Custom
"""

EXAMPLES = r"""
- name: Create RAM policy
  stevefulme1.alibaba_cloud.ram_policy:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    policy_name: ecs-readonly
    policy_document: '{"Version":"1","Statement":[...]}'
"""

RETURN = r"""
policy:
  description: RAM policy details.
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
        policy_name=dict(type="str", required=True),
        policy_document=dict(type="str"),
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

    params = {}
    if module.params.get("policy_name") is not None:
        params["PolicyName"] = module.params["policy_name"]
    if module.params.get("policy_document") is not None:
        params["PolicyDocument"] = module.params["policy_document"]
    if module.params.get("policy_type") is not None:
        params["PolicyType"] = module.params["policy_type"]

    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "ListPolicies",
            params,
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
                    "CreatePolicy",
                    params,
                    service_endpoint="ram.aliyuncs.com",
                    api_version="2015-05-01",
                )
                changed = True
                module.exit_json(changed=changed, ram_policy=result)
            else:
                module.exit_json(
                    changed=False,
                    ram_policy=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeletePolicy",
                    params,
                    service_endpoint="ram.aliyuncs.com",
                    api_version="2015-05-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
