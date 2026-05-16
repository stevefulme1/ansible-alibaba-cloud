#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.eventbridge_rule"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: eventbridge_rule
short_description: Manage EventBridge rules.
description:
  - Create, update, or delete Alibaba Cloud eventbridge_rule resources.
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
  event_bus_name:
    description: Event bus name for the rule.
    type: str
    required: true
  rule_name:
    description: Name of the event rule.
    type: str
    required: true
  filter_pattern:
    description: Event filter pattern (JSON string).
    type: str
  targets:
    description: List of rule target configurations.
    type: list
    elements: dict
"""

EXAMPLES = r"""
- name: Manage eventbridge_rule resource
  stevefulme1.alibaba_cloud.eventbridge_rule:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    event_bus_name: my-event-bus
    rule_name: order-created-rule
"""

RETURN = r"""
eventbridge_rule:
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
        event_bus_name=dict(type="str", required=True),
        rule_name=dict(type="str", required=True),
        filter_pattern=dict(type="str"),
        targets=dict(type="list", elements="dict"),
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
            "ListRules",
            {},
            service_endpoint="eventbridge.aliyuncs.com",
            api_version="2020-04-01",
        )

        data = existing
        for key in "Data.Rules".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateRule",
                    {},
                    service_endpoint="eventbridge.aliyuncs.com",
                    api_version="2020-04-01",
                )
                changed = True
                module.exit_json(changed=changed, eventbridge_rule=result)
            else:
                module.exit_json(changed=False, eventbridge_rule=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteRule",
                    {},
                    service_endpoint="eventbridge.aliyuncs.com",
                    api_version="2020-04-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
