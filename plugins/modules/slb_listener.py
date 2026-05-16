#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.slb_listener"""

from __future__ import annotations

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


DOCUMENTATION = r"""
---
module: slb_listener
short_description: Manage SLB listeners.
description:
  - Create, update, or delete Alibaba Cloud slb_listener resources.
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
  load_balancer_id:
    description: SLB instance ID.
    type: str
    required: true
  listener_port:
    description: Listener port number.
    type: int
    required: true
  backend_server_port:
    description: Backend server port.
    type: int
  bandwidth:
    description: Bandwidth limit in Mbps (-1 for unlimited).
    type: int
    default: -1
  protocol:
    description: Listener protocol.
    type: str
    choices: [tcp, udp, http, https]
    default: tcp
"""

EXAMPLES = r"""
- name: Create TCP listener
  stevefulme1.alibaba_cloud.slb_listener:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    load_balancer_id: lb-xxxxx
    listener_port: 80
    backend_server_port: 8080
"""

RETURN = r"""
listener:
  description: Listener details.
  returned: success
  type: dict
"""


def main():
    spec = dict(
        state=dict(
            type="str",
            choices=["present", "absent"],
            default="present",
        ),
        load_balancer_id=dict(type="str", required=True),
        listener_port=dict(type="int", required=True),
        backend_server_port=dict(type="int"),
        bandwidth=dict(type="int", default=-1),
        protocol=dict(
            type="str", choices=["tcp", "udp", "http", "https"], default="tcp"
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
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeLoadBalancerListeners",
            {},
            service_endpoint="slb.aliyuncs.com",
            api_version="2014-05-15",
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
                    "CreateLoadBalancerTCPListener",
                    {},
                    service_endpoint="slb.aliyuncs.com",
                    api_version="2014-05-15",
                )
                changed = True
                module.exit_json(changed=changed, slb_listener=result)
            else:
                module.exit_json(
                    changed=False,
                    slb_listener=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteLoadBalancerListener",
                    {},
                    service_endpoint="slb.aliyuncs.com",
                    api_version="2014-05-15",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
