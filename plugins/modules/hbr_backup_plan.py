#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.hbr_backup_plan"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: hbr_backup_plan
short_description: Manage HBR backup plans.
description:
  - Create or delete manage hbr backup plans.
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
  plan_id:
    description: Backup plan ID.
    type: str
  plan_name:
    description: Backup plan name.
    type: str
  vault_id:
    description: Associated vault ID.
    type: str
  schedule:
    description: Backup schedule expression.
    type: str
  retention:
    description: Retention period in days.
    type: int"""

EXAMPLES = r"""
- name: Manage HBR backup plans.
  stevefulme1.alibaba_cloud.hbr_backup_plan:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
hbr_backup_plan:
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
        plan_id=dict(type="str"),
        plan_name=dict(type="str"),
        vault_id=dict(type="str"),
        schedule=dict(type="str"),
        retention=dict(type="int"),
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
            "DescribeBackupPlans",
            {},
            service_endpoint="hbr.aliyuncs.com",
            api_version="2017-09-08",
        )

        data = existing
        for key in "BackupPlans.BackupPlan".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateBackupPlan",
                    {},
                    service_endpoint="hbr.aliyuncs.com",
                    api_version="2017-09-08",
                )
                changed = True
                module.exit_json(changed=changed, hbr_backup_plan=result)
            else:
                module.exit_json(changed=False, hbr_backup_plan=data[0])

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteBackupPlan",
                    {},
                    service_endpoint="hbr.aliyuncs.com",
                    api_version="2017-09-08",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
