#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sls_alert"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sls_alert
short_description: Manage SLS alert rules.
description:
  - Create, update, or delete Alibaba Cloud SLS alert resources.
  - Supports check mode and is idempotent.version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  state:
    description: Desired state of the resource.
    type: str
    choices: [present, absent]
    default: present
  project_name:
    description: Log Service project name.
    type: str
  alert_name:
    description: Name of the alert rule.
    type: str
  alert_display_name:
    description: Display name of the alert.
    type: str
  schedule_interval:
    description: Evaluation interval, e.g. C(5m).
    type: str
  condition:
    description: Trigger condition expression.
    type: str
  dashboard:
    description: Associated dashboard name.
    type: str
"""

EXAMPLES = r"""
- name: Create a SLS alert
  stevefulme1.alibaba_cloud.sls_alert:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    project_name: example-value
    alert_name: example-value
"""

RETURN = r"""
sls_alert:
  description: Sls alert details.
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
        project_name=dict(type="str"),
        alert_name=dict(type="str"),
        alert_display_name=dict(type="str"),
        schedule_interval=dict(type="str"),
        condition=dict(type="str"),
        dashboard=dict(type="str"),
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
            "DescribeAlert",
            {},
            service_endpoint="sls.{region_id}.aliyuncs.com",
            api_version="2020-12-30",
        )

        data = existing
        for key in "Alerts.Alert".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateAlert",
                    {},
                    service_endpoint="sls.{region_id}.aliyuncs.com",
                    api_version="2020-12-30",
                )
                changed = True
                module.exit_json(changed=changed, sls_alert=result)
            else:
                module.exit_json(
                    changed=False,
                    sls_alert=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteAlert",
                    {},
                    service_endpoint="sls.{region_id}.aliyuncs.com",
                    api_version="2020-12-30",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
