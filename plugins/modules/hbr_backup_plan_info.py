#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.hbr_backup_plan_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: hbr_backup_plan_info
short_description: Query Hybrid Backup Recovery backup plans.
description:
  - Retrieve information about Alibaba Cloud HBR backup plans.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  vault_id:
    description: Backup vault ID.
    type: str
  plan_id:
    description: Filter by backup plan ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all HBR backup plans
  stevefulme1.alibaba_cloud.hbr_backup_plan_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    vault_id: v-123

- name: Query specific HBR backup plan
  stevefulme1.alibaba_cloud.hbr_backup_plan_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    plan_id: plan-123
"""

RETURN = r"""
hbr_backup_plans:
  description: List of HBR backup plans.
  returned: success
  type: list
  elements: dict
  sample:
    - plan_id: plan-123
      plan_name: daily-backup
      vault_id: v-123
      schedule: "I|1602673264|PT2H"
      retention: 7
      disabled: false
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        vault_id=dict(type="str"),
        plan_id=dict(type="str"),
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
    if module.params.get("vault_id"):
        params["VaultId"] = module.params["vault_id"]
    if module.params.get("plan_id"):
        params["PlanId"] = module.params["plan_id"]

    try:
        result = client.get(
            "DescribeBackupPlans",
            params,
            service_endpoint="hbr.aliyuncs.com",
            api_version="2017-09-08",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "BackupPlans.BackupPlan".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, hbr_backup_plans=data)


if __name__ == "__main__":
    main()
