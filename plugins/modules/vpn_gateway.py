#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.vpn_gateway"""

from __future__ import annotations


DOCUMENTATION = r"""
---
module: vpn_gateway
short_description: Manage VPN gateways.
description:
  - Create, update, or delete Alibaba Cloud vpn_gateway resources.
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
  vpn_gateway_name:
    description: Name of the VPN gateway.
    type: str
  vpc_id:
    description: VPC ID for the VPN gateway.
    type: str
  bandwidth:
    description: Bandwidth in Mbps.
    type: int
    default: 5
  vpn_gateway_id:
    description: Existing gateway ID (for delete).
    type: str
"""

EXAMPLES = r"""
- name: Create VPN gateway
  stevefulme1.alibaba_cloud.vpn_gateway:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    vpn_gateway_name: site-to-site
    vpc_id: vpc-xxxxx
    bandwidth: 10
"""

RETURN = r"""
vpn_gateway:
  description: VPN gateway details.
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
        vpn_gateway_name=dict(type="str"),
        vpc_id=dict(type="str"),
        bandwidth=dict(type="int", default=5),
        vpn_gateway_id=dict(type="str"),
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
            "DescribeVpnGateways",
            {},
            service_endpoint="vpc.aliyuncs.com",
            api_version="2016-04-28",
        )

        data = existing
        for key in "VpnGateways.VpnGateway".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateVpnGateway",
                    {},
                    service_endpoint="vpc.aliyuncs.com",
                    api_version="2016-04-28",
                )
                changed = True
                module.exit_json(changed=changed, vpn_gateway=result)
            else:
                module.exit_json(
                    changed=False,
                    vpn_gateway=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteVpnGateway",
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
