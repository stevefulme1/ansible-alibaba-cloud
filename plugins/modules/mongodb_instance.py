#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.mongodb_instance"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: mongodb_instance
short_description: Manage MongoDB instances.
description:
  - Create, update, or delete Alibaba Cloud MongoDB instances.
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
    description: ID of an existing MongoDB instance.
    type: str
  db_instance_class:
    description: Instance specification.
    type: str
  db_instance_storage:
    description: Storage size in GB.
    type: int
  engine:
    description: Database engine.
    type: str
  engine_version:
    description: Engine version.
    type: str
  db_instance_description:
    description: Instance description.
    type: str
  account_password:
    description: Root account password.
    type: str
"""

EXAMPLES = r"""
- name: Manage MongoDB instances
  stevefulme1.alibaba_cloud.mongodb_instance:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
mongodb_instance:
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
        db_instance_class=dict(type="str"),
        db_instance_storage=dict(type="int"),
        engine=dict(type="str"),
        engine_version=dict(type="str"),
        db_instance_description=dict(type="str"),
        account_password=dict(type="str", no_log=True),
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
    if module.params.get("db_instance_id") is not None:
        params["DBInstanceId"] = module.params["db_instance_id"]
    if module.params.get("db_instance_class") is not None:
        params["DBInstanceClass"] = module.params["db_instance_class"]
    if module.params.get("db_instance_storage") is not None:
        params["DBInstanceStorage"] = module.params["db_instance_storage"]
    if module.params.get("engine") is not None:
        params["Engine"] = module.params["engine"]
    if module.params.get("engine_version") is not None:
        params["EngineVersion"] = module.params["engine_version"]
    if module.params.get("db_instance_description") is not None:
        params["DBInstanceDescription"] = module.params["db_instance_description"]
    if module.params.get("account_password") is not None:
        params["AccountPassword"] = module.params["account_password"]


    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeDBInstances",
            params,
            service_endpoint="mongodb.aliyuncs.com",
            api_version="2015-12-01",
        )

        data = existing
        for key in "DBInstances.DBInstance".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateDBInstance",
                    params,
                    service_endpoint="mongodb.aliyuncs.com",
                    api_version="2015-12-01",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    mongodb_instance=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    mongodb_instance=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteDBInstance",
                    params,
                    service_endpoint="mongodb.aliyuncs.com",
                    api_version="2015-12-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
