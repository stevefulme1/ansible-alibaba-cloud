#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.vpn_connection_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: vpn_connection_info
short_description: Query VPN connections.
description:
  - Retrieve information about Alibaba Cloud VPN connections.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  vpn_connection_id:
    description: Filter by VPN connection ID.
    type: str
  vpn_gateway_id:
    description: Filter by VPN gateway ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all VPN connections
  stevefulme1.alibaba_cloud.vpn_connection_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query VPN connections for a gateway
  stevefulme1.alibaba_cloud.vpn_connection_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    vpn_gateway_id: vpn-xxxxx
"""

RETURN = r"""
vpn_connections:
  description: List of VPN connections.
  returned: success
  type: list
  elements: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        vpn_connection_id=dict(type="str"),
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

    params = {}
    if module.params.get("vpn_connection_id"):
        params["VpnConnectionId"] = module.params["vpn_connection_id"]
    if module.params.get("vpn_gateway_id"):
        params["VpnGatewayId"] = module.params["vpn_gateway_id"]

    try:
        result = client.get(
            "DescribeVpnConnections",
            params,
            service_endpoint="vpc.aliyuncs.com",
            api_version="2016-04-28",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "VpnConnections.VpnConnection".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, vpn_connections=data)


if __name__ == "__main__":
    main()
