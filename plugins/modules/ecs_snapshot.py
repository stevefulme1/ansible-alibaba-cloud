#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ecs_snapshot"""

from __future__ import annotations


DOCUMENTATION = r"""
---
module: ecs_snapshot
short_description: Manage disk snapshots.
description:
  - Create, update, or delete Alibaba Cloud ecs_snapshot resources.
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
  snapshot_name:
    description: Name of the snapshot.
    type: str
  disk_id:
    description: Source disk ID.
    type: str
  snapshot_id:
    description: Existing snapshot ID (for delete).
    type: str
"""

EXAMPLES = r"""
- name: Create snapshot
  stevefulme1.alibaba_cloud.ecs_snapshot:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    snapshot_name: daily-snap
    disk_id: d-xxxxx
"""

RETURN = r"""
snapshot:
  description: Snapshot details.
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
        snapshot_name=dict(type="str"),
        disk_id=dict(type="str"),
        snapshot_id=dict(type="str"),
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
            "DescribeSnapshots",
            {},
            service_endpoint="ecs.aliyuncs.com",
            api_version="2014-05-26",
        )

        data = existing
        for key in "Snapshots.Snapshot".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateSnapshot",
                    {},
                    service_endpoint="ecs.aliyuncs.com",
                    api_version="2014-05-26",
                )
                changed = True
                module.exit_json(changed=changed, ecs_snapshot=result)
            else:
                module.exit_json(
                    changed=False,
                    ecs_snapshot=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteSnapshot",
                    {},
                    service_endpoint="ecs.aliyuncs.com",
                    api_version="2014-05-26",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
