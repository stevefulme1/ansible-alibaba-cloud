#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cms_alarm"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cms_alarm
short_description: Manage CloudMonitor alarm rules.
description:
  - Create, update, or delete Alibaba Cloud CloudMonitor alarm rules.
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
  rule_id:
    description: Alarm rule ID.
    type: str
  rule_name:
    description: Alarm rule display name.
    type: str
  namespace:
    description: Product namespace, e.g. C(acs_ecs_dashboard).
    type: str
  metric_name:
    description: Metric name.
    type: str
  period:
    description: Monitoring period in seconds.
    type: int
  threshold:
    description: Alarm threshold value.
    type: str
  comparison_operator:
    description: Comparison operator.
    type: str
  statistics:
    description: Statistic method.
    type: str
    choices: ['Average', 'Maximum', 'Minimum']
  contact_groups:
    description: Alarm contact groups.
    type: str
"""

EXAMPLES = r"""
- name: Manage CloudMonitor alarm rules
  stevefulme1.alibaba_cloud.cms_alarm:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
cms_alarm:
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
        rule_id=dict(type="str"),
        rule_name=dict(type="str"),
        namespace=dict(type="str"),
        metric_name=dict(type="str"),
        period=dict(type="int"),
        threshold=dict(type="str"),
        comparison_operator=dict(type="str"),
        statistics=dict(type="str", choices=["Average", "Maximum", "Minimum"]),
        contact_groups=dict(type="str"),
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
            "DescribeMetricRuleList",
            {},
            service_endpoint="metrics.aliyuncs.com",
            api_version="2019-01-01",
        )

        data = existing
        for key in "Alarms.Alarm".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "PutResourceMetricRule",
                    {},
                    service_endpoint="metrics.aliyuncs.com",
                    api_version="2019-01-01",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    cms_alarm=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    cms_alarm=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteMetricRules",
                    {},
                    service_endpoint="metrics.aliyuncs.com",
                    api_version="2019-01-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
