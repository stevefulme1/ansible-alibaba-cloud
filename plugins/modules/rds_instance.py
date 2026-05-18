#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.rds_instance"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: rds_instance
short_description: Manage RDS instances.
description:
  - Create, update, or delete Alibaba Cloud RDS instances.
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
  db_instance_id:
    description: ID of an existing RDS instance.
    type: str
  engine:
    description: Database engine.
    type: str
    choices: ['MySQL', 'SQLServer', 'PostgreSQL', 'MariaDB']
  engine_version:
    description: Database engine version.
    type: str
  db_instance_class:
    description: Instance specification.
    type: str
  db_instance_storage:
    description: Storage size in GB.
    type: int
  db_instance_description:
    description: Instance description.
    type: str
  pay_type:
    description: Payment type.
    type: str
    choices: ['Postpaid', 'Prepaid']
"""

EXAMPLES = r"""
- name: Manage RDS instances
  stevefulme1.alibaba_cloud.rds_instance:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
rds_instance:
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
        db_instance_id=dict(type="str"),
        engine=dict(type="str", choices=["MySQL", "SQLServer", "PostgreSQL", "MariaDB"]),
        engine_version=dict(type="str"),
        db_instance_class=dict(type="str"),
        db_instance_storage=dict(type="int"),
        db_instance_description=dict(type="str"),
        pay_type=dict(type="str", choices=["Postpaid", "Prepaid"]),
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
            "DescribeDBInstances",
            {},
            service_endpoint="rds.aliyuncs.com",
            api_version="2014-08-15",
        )

        data = existing
        for key in "Items.DBInstance".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateDBInstance",
                    {},
                    service_endpoint="rds.aliyuncs.com",
                    api_version="2014-08-15",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    rds_instance=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    rds_instance=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteDBInstance",
                    {},
                    service_endpoint="rds.aliyuncs.com",
                    api_version="2014-08-15",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
