#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.alidns_gtm_address_pool_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: alidns_gtm_address_pool_info
short_description: Query GTM address pools.
description:
  - Retrieve information about Alibaba Cloud GTM address pools.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  instance_id:
    description: Filter by GTM instance ID.
    type: str
  addr_pool_id:
    description: Filter by address pool ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all GTM address pools
  stevefulme1.alibaba_cloud.alidns_gtm_address_pool_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific GTM address pool
  stevefulme1.alibaba_cloud.alidns_gtm_address_pool_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: gtm-instance-id
    addr_pool_id: pool-id
"""

RETURN = r"""
alidns_gtm_address_pools:
  description: List of GTM address pools.
  returned: success
  type: list
  elements: dict
  sample:
    - addr_pool_id: pool-123
      name: pool-name
      addr_pool_type: IPV4
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        instance_id=dict(type="str"),
        addr_pool_id=dict(type="str"),
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
    if module.params.get("instance_id"):
        params["InstanceId"] = module.params["instance_id"]
    if module.params.get("addr_pool_id"):
        params["AddrPoolId"] = module.params["addr_pool_id"]

    try:
        result = client.get(
            "DescribeDnsGtmInstanceAddressPool",
            params,
            service_endpoint="alidns.aliyuncs.com",
            api_version="2015-01-09",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Addrs.Addr".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, alidns_gtm_address_pools=data)


if __name__ == "__main__":
    main()
