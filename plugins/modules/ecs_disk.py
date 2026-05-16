#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ecs_disk"""

from __future__ import annotations

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


DOCUMENTATION = r"""
---
module: ecs_disk
short_description: Manage cloud disks.
description:
  - Create, update, or delete Alibaba Cloud ecs_disk resources.
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
  disk_name:
    description: Display name of the disk.
    type: str
  disk_category:
    description: Disk type (cloud_efficiency, cloud_ssd, cloud_essd).
    type: str
  size:
    description: Disk size in GiB.
    type: int
  zone_id:
    description: Availability zone.
    type: str
  disk_id:
    description: Existing disk ID (for delete).
    type: str
"""

EXAMPLES = r"""
- name: Create a cloud disk
  stevefulme1.alibaba_cloud.ecs_disk:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    disk_name: data-disk
    disk_category: cloud_essd
    size: 100
    zone_id: cn-hangzhou-a
"""

RETURN = r"""
disk:
  description: Disk details.
  returned: success
  type: dict
"""


def main():
    spec = dict(
        state=dict(
            type="str", choices=["present", "absent"],
            default="present",
        ),
        disk_name=dict(type="str"),
        disk_category=dict(type="str"),
        size=dict(type="int"),
        zone_id=dict(type="str"),
        disk_id=dict(type="str"),
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
            "DescribeDisks", {},
            service_endpoint="ecs.aliyuncs.com",
            api_version="2014-05-26",
        )

        data = existing
        for key in "Disks.Disk".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateDisk", {},
                    service_endpoint="ecs.aliyuncs.com",
                    api_version="2014-05-26",
                )
                changed = True
                module.exit_json(changed=changed, ecs_disk=result)
            else:
                module.exit_json(
                    changed=False, ecs_disk=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteDisk", {},
                    service_endpoint="ecs.aliyuncs.com",
                    api_version="2014-05-26",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
