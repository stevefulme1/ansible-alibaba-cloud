#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.hbr_restore_job"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: hbr_restore_job
short_description: Manage HBR restore jobs.
description:
  - Create or delete manage hbr restore jobs.
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
  restore_id:
    description: Restore job ID.
    type: str
  vault_id:
    description: Source vault ID.
    type: str
  snapshot_id:
    description: Snapshot to restore from.
    type: str
  target_instance_id:
    description: Target instance for restoration.
    type: str"""

EXAMPLES = r"""
- name: Manage HBR restore jobs.
  stevefulme1.alibaba_cloud.hbr_restore_job:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
hbr_restore_job:
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
        restore_id=dict(type="str"),
        vault_id=dict(type="str"),
        snapshot_id=dict(type="str"),
        target_instance_id=dict(type="str"),
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
            "DescribeRestoreJobs2",
            {},
            service_endpoint="hbr.aliyuncs.com",
            api_version="2017-09-08",
        )

        data = existing
        for key in "RestoreJobs.RestoreJob".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateRestoreJob",
                    {},
                    service_endpoint="hbr.aliyuncs.com",
                    api_version="2017-09-08",
                )
                changed = True
                module.exit_json(changed=changed, hbr_restore_job=result)
            else:
                module.exit_json(changed=False, hbr_restore_job=data[0])

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "CancelRestoreJob",
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
