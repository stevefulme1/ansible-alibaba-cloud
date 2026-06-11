#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sgw_share_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sgw_share_info
short_description: Query Storage Gateway file shares.
description:
  - Retrieve information about Alibaba Cloud Storage Gateway file shares.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  gateway_id:
    description: Storage gateway ID.
    type: str
    required: true
  share_name:
    description: Filter by file share name.
    type: str
"""

EXAMPLES = r"""
- name: Query all Storage Gateway file shares
  stevefulme1.alibaba_cloud.sgw_share_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    gateway_id: gw-xxxxx

- name: Query specific file share
  stevefulme1.alibaba_cloud.sgw_share_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    gateway_id: gw-xxxxx
    share_name: myshare
"""

RETURN = r"""
sgw_shares:
  description: List of Storage Gateway file shares.
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
        share_name=dict(type="str"),
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
    if module.params.get("share_name"):
        params["ShareName"] = module.params["share_name"]

    try:
        result = client.get(
            "DescribeGatewayFileShares",
            params,
            service_endpoint="sgw.aliyuncs.com",
            api_version="2018-05-11",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "FileShares.FileShare".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, sgw_shares=data)


if __name__ == "__main__":
    main()
