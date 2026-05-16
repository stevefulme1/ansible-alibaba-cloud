#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ahas_guard_rule"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ahas_guard_rule
short_description: Manage system guard rule.
description:
  - Create, update, or delete Alibaba Cloud ahas_guard_rule resources.
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
  app_name:
    description: Application name.
    type: str
  namespace:
    description: AHAS namespace.
    type: str
  metric_type:
    description: System metric type (0=load, 1=rt, 2=thread, 3=qps, 4=cpu).
    type: int
  threshold:
    description: System guard threshold.
    type: int
  rule_id:
    description: Rule ID for delete.
    type: str
"""

EXAMPLES = r"""
- name: Manage ahas_guard_rule
  stevefulme1.alibaba_cloud.ahas_guard_rule:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    app_name: my-app
    metric_type: 4
    threshold: 80
"""

RETURN = r"""
ahas_guard_rule:
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
        app_name=dict(type="str"),
        namespace=dict(type="str"),
        metric_type=dict(type="int"),
        threshold=dict(type="int"),
        rule_id=dict(type="str"),
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
            "ListSystemRules",
            {},
            service_endpoint="ahas.aliyuncs.com",
            api_version="2019-09-01",
        )

        data = result
        for key in ["Data", "Datas"]:
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateSystemRule",
                    {},
                    service_endpoint="ahas.aliyuncs.com",
                    api_version="2019-09-01",
                )
                changed = True
                module.exit_json(changed=changed, ahas_guard_rule=result)
            else:
                module.exit_json(
                    changed=False,
                    ahas_guard_rule=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteSystemRule",
                    {},
                    service_endpoint="ahas.aliyuncs.com",
                    api_version="2019-09-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
