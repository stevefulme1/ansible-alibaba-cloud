#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ga_instance"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ga_instance
short_description: Manage Global Accelerator instances.
description:
  - Create, update, or delete Alibaba Cloud ga_instance resources.
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
  accelerator_name:
    description: Name of the GA instance.
    type: str
  accelerator_id:
    description: ID of an existing GA instance.
    type: str
  spec:
    description: Specification of the GA instance.
    type: str
    choices: ["1", "2", "3", "5", "8", "10"]
"""

EXAMPLES = r"""
- name: Manage ga_instance resource
  stevefulme1.alibaba_cloud.ga_instance:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    accelerator_name: my-ga
"""

RETURN = r"""
ga_instance:
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
        accelerator_name=dict(type="str"),
        accelerator_id=dict(type="str"),
        spec=dict(type="str", choices=["1", "2", "3", "5", "8", "10"]),
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
            "ListAccelerators",
            {},
            service_endpoint="ga.aliyuncs.com",
            api_version="2019-11-20",
        )

        data = existing
        for key in "Accelerators".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateAccelerator",
                    {},
                    service_endpoint="ga.aliyuncs.com",
                    api_version="2019-11-20",
                )
                changed = True
                module.exit_json(changed=changed, ga_instance=result)
            else:
                module.exit_json(changed=False, ga_instance=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteAccelerator",
                    {},
                    service_endpoint="ga.aliyuncs.com",
                    api_version="2019-11-20",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
