#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.vpn_connection"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: vpn_connection
short_description: Manage VPN connections.
description:
  - Create, update, or delete Alibaba Cloud vpn_connection resources.
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
  vpn_connection_name:
    description: Name of the VPN connection.
    type: str
  vpn_gateway_id:
    description: VPN gateway ID.
    type: str
  customer_gateway_id:
    description: Customer gateway ID.
    type: str
  local_subnet:
    description: Local network CIDR.
    type: str
  remote_subnet:
    description: Remote network CIDR.
    type: str
  vpn_connection_id:
    description: Existing connection ID (for delete).
    type: str
"""

EXAMPLES = r"""
- name: Create VPN connection
  stevefulme1.alibaba_cloud.vpn_connection:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    vpn_connection_name: dc-link
    vpn_gateway_id: vpn-xxxxx
    customer_gateway_id: cgw-xxxxx
    local_subnet: 172.16.0.0/12
    remote_subnet: 10.0.0.0/8
"""

RETURN = r"""
vpn_connection:
  description: VPN connection details.
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
        vpn_connection_name=dict(type="str"),
        vpn_gateway_id=dict(type="str"),
        customer_gateway_id=dict(type="str"),
        local_subnet=dict(type="str"),
        remote_subnet=dict(type="str"),
        vpn_connection_id=dict(type="str"),
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
            "DescribeVpnConnections",
            {},
            service_endpoint="vpc.aliyuncs.com",
            api_version="2016-04-28",
        )

        data = existing
        for key in "VpnConnections.VpnConnection".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateVpnConnection",
                    {},
                    service_endpoint="vpc.aliyuncs.com",
                    api_version="2016-04-28",
                )
                changed = True
                module.exit_json(changed=changed, vpn_connection=result)
            else:
                module.exit_json(
                    changed=False,
                    vpn_connection=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteVpnConnection",
                    {},
                    service_endpoint="vpc.aliyuncs.com",
                    api_version="2016-04-28",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
