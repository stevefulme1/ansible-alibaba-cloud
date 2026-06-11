#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sgw_cache_disk_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sgw_cache_disk_info
short_description: Query Storage Gateway cache disks.
description:
  - Retrieve information about Alibaba Cloud Storage Gateway cache disks.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  gateway_id:
    description: Storage gateway ID.
    type: str
    required: true
"""

EXAMPLES = r"""
- name: Query Storage Gateway cache disks
  stevefulme1.alibaba_cloud.sgw_cache_disk_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    gateway_id: gw-xxxxx
"""

RETURN = r"""
sgw_cache_disks:
  description: List of Storage Gateway cache disks.
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
        gateway_id=dict(type="str", required=True),
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

    params = {
        "GatewayId": module.params["gateway_id"],
    }

    try:
        result = client.get(
            "DescribeGatewayCaches",
            params,
            service_endpoint="sgw.aliyuncs.com",
            api_version="2018-05-11",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Caches.Cache".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, sgw_cache_disks=data)


if __name__ == "__main__":
    main()
