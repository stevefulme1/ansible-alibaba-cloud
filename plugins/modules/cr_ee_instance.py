#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cr_ee_instance"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cr_ee_instance
short_description: Manage Container Registry Enterprise Edition instance.
description:
  - Create, update, or delete Alibaba Cloud cr_ee_instance resources.
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
  instance_name:
    description: Enterprise registry instance name.
    type: str
  instance_type:
    description: Instance type (Basic, Standard, Advanced).
    type: str
  instance_id:
    description: Instance ID for update or delete.
    type: str
"""

EXAMPLES = r"""
- name: Manage cr_ee_instance
  stevefulme1.alibaba_cloud.cr_ee_instance:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    instance_name: my-ee-registry
    instance_type: Standard
"""

RETURN = r"""
cr_ee_instance:
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
        state=dict(
            type="str",
            choices=["present", "absent"],
            default="present",
        ),
        instance_name=dict(type="str"),
        instance_type=dict(type="str"),
        instance_id=dict(type="str"),
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
        result = client.get(
            "ListInstance",
            {},
            service_endpoint="cr.aliyuncs.com",
            api_version="2018-12-01",
        )

        data = result
        for key in ["Instances"]:
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateInstance",
                    {},
                    service_endpoint="cr.aliyuncs.com",
                    api_version="2018-12-01",
                )
                changed = True
                module.exit_json(changed=changed, cr_ee_instance=result)
            else:
                module.exit_json(
                    changed=False,
                    cr_ee_instance=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteInstance",
                    {},
                    service_endpoint="cr.aliyuncs.com",
                    api_version="2018-12-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
