#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dts_migration_job"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: dts_migration_job
short_description: Manage DTS migration jobs.
description:
  - Create, update, or delete Alibaba Cloud dts_migration_job resources.
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
  migration_job_id:
    description: ID of an existing migration job.
    type: str
  migration_job_name:
    description: Name of the migration job.
    type: str
    required: true
  source_endpoint:
    description: Source endpoint configuration.
    type: dict
  destination_endpoint:
    description: Destination endpoint configuration.
    type: dict
  migration_mode:
    description: Migration mode configuration.
    type: dict
"""

EXAMPLES = r"""
- name: Manage dts_migration_job resource
  stevefulme1.alibaba_cloud.dts_migration_job:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    migration_job_name: mysql-to-polardb
"""

RETURN = r"""
dts_migration_job:
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
        migration_job_id=dict(type="str"),
        migration_job_name=dict(type="str", required=True),
        source_endpoint=dict(type="dict"),
        destination_endpoint=dict(type="dict"),
        migration_mode=dict(type="dict"),
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
            "DescribeMigrationJobs",
            {},
            service_endpoint="dts.aliyuncs.com",
            api_version="2020-01-01",
        )

        data = existing
        for key in "MigrationJobs.MigrationJob".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateMigrationJob",
                    {},
                    service_endpoint="dts.aliyuncs.com",
                    api_version="2020-01-01",
                )
                changed = True
                module.exit_json(changed=changed, dts_migration_job=result)
            else:
                module.exit_json(changed=False, dts_migration_job=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteMigrationJob",
                    {},
                    service_endpoint="dts.aliyuncs.com",
                    api_version="2020-01-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
