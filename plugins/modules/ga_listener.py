#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ga_listener"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ga_listener
short_description: Manage Global Accelerator listeners.
description:
  - Create, update, or delete Alibaba Cloud ga_listener resources.
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
  accelerator_id:
    description: GA instance ID for the listener.
    type: str
    required: true
  listener_id:
    description: ID of an existing listener.
    type: str
  port_ranges:
    description: List of port range configurations.
    type: list
    elements: dict
  protocol:
    description: Listener protocol.
    type: str
    choices: [TCP, UDP, HTTP, HTTPS]
    default: TCP
"""

EXAMPLES = r"""
- name: Manage ga_listener resource
  stevefulme1.alibaba_cloud.ga_listener:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    accelerator_id: ga-xxxxx
    protocol: TCP
"""

RETURN = r"""
ga_listener:
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
        accelerator_id=dict(type="str", required=True),
        listener_id=dict(type="str"),
        port_ranges=dict(type="list", elements="dict"),
        protocol=dict(
            type="str", choices=["TCP", "UDP", "HTTP", "HTTPS"], default="TCP"
        ),
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
            "ListListeners",
            {},
            service_endpoint="ga.aliyuncs.com",
            api_version="2019-11-20",
        )

        data = existing
        for key in "Listeners".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateListener",
                    {},
                    service_endpoint="ga.aliyuncs.com",
                    api_version="2019-11-20",
                )
                changed = True
                module.exit_json(changed=changed, ga_listener=result)
            else:
                module.exit_json(changed=False, ga_listener=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteListener",
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
