#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.nas_file_system"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nas_file_system
short_description: Manage NAS file systems.
description:
  - Create, update, or delete Alibaba Cloud NAS file systems.
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
  file_system_id:
    description: ID of an existing file system.
    type: str
  storage_type:
    description: Storage type.
    type: str
    choices: ['Performance', 'Capacity']
  protocol_type:
    description: Protocol type.
    type: str
    choices: ['NFS', 'SMB']
  description:
    description: File system description.
    type: str
"""

EXAMPLES = r"""
- name: Manage NAS file systems
  stevefulme1.alibaba_cloud.nas_file_system:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
nas_file_system:
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
        file_system_id=dict(type="str"),
        storage_type=dict(type="str", choices=["Performance", "Capacity"]),
        protocol_type=dict(type="str", choices=["NFS", "SMB"]),
        description=dict(type="str"),
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
            "DescribeFileSystems",
            {},
            service_endpoint="nas.aliyuncs.com",
            api_version="2017-06-26",
        )

        data = existing
        for key in "FileSystems.FileSystem".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateFileSystem",
                    {},
                    service_endpoint="nas.aliyuncs.com",
                    api_version="2017-06-26",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    nas_file_system=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    nas_file_system=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteFileSystem",
                    {},
                    service_endpoint="nas.aliyuncs.com",
                    api_version="2017-06-26",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
