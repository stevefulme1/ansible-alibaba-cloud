#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.eventbridge_rule_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: eventbridge_rule_info
short_description: Query EventBridge rules.
description:
  - Retrieve information about Alibaba Cloud EventBridge rules.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  event_bus_name:
    description: Event bus name.
    type: str
  rule_name:
    description: Filter by rule name.
    type: str
"""

EXAMPLES = r"""
- name: Query all EventBridge rules
  stevefulme1.alibaba_cloud.eventbridge_rule_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    event_bus_name: my-event-bus

- name: Query specific EventBridge rule
  stevefulme1.alibaba_cloud.eventbridge_rule_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    event_bus_name: my-event-bus
    rule_name: my-rule
"""

RETURN = r"""
eventbridge_rules:
  description: List of EventBridge rules.
  returned: success
  type: list
  elements: dict
  sample:
    - rule_name: my-rule
      description: Event routing rule
      status: ENABLE
      filter_pattern: "{\"source\":[\"myapp\"]}"
      targets:
        - id: "1"
          type: acs.fc
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        event_bus_name=dict(type="str"),
        rule_name=dict(type="str"),
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

    params = {}
    if module.params.get("event_bus_name"):
        params["EventBusName"] = module.params["event_bus_name"]
    if module.params.get("rule_name"):
        params["RuleName"] = module.params["rule_name"]

    try:
        result = client.get(
            "ListRules",
            params,
            service_endpoint="eventbridge.aliyuncs.com",
            api_version="2020-04-01",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Data.Rules".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, eventbridge_rules=data)


if __name__ == "__main__":
    main()
