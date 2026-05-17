#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.rds_database"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: rds_database
short_description: Manage RDS databases.
description:
  - Create or delete databases within an Alibaba Cloud RDS instance.
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
    description: RDS instance ID.
    type: str
  db_name:
    description: Database name.
    type: str
  character_set_name:
    description: Character set, e.g. C(utf8mb4).
    type: str
  db_description:
    description: Database description.
    type: str
"""

EXAMPLES = r"""
- name: Manage RDS databases
  stevefulme1.alibaba_cloud.rds_database:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
rds_database:
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
        db_name=dict(type="str"),
        character_set_name=dict(type="str"),
        db_description=dict(type="str"),
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
    if module.params.get("db_name") is not None:
        params["DBName"] = module.params["db_name"]
    if module.params.get("character_set_name") is not None:
        params["CharacterSetName"] = module.params["character_set_name"]
    if module.params.get("db_description") is not None:
        params["DBDescription"] = module.params["db_description"]

    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeDatabases",
            params,
            service_endpoint="rds.aliyuncs.com",
            api_version="2014-08-15",
        )

        data = existing
        for key in "Databases.Database".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateDatabase",
                    params,
                    service_endpoint="rds.aliyuncs.com",
                    api_version="2014-08-15",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    rds_database=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    rds_database=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteDatabase",
                    params,
                    service_endpoint="rds.aliyuncs.com",
                    api_version="2014-08-15",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
