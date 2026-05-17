#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.smart_ag_instance"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: smart_ag_instance
short_description: Manage Smart Access Gateway instance.
description:
  - Create, update, or delete Alibaba Cloud smart_ag_instance resources.
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
  smart_ag_name:
    description: Smart AG instance name.
    type: str
  max_band_width:
    description: Maximum bandwidth in Mbps.
    type: int
  smart_ag_id:
    description: Instance ID for delete.
    type: str
"""

EXAMPLES = r"""
- name: Manage smart_ag_instance
  stevefulme1.alibaba_cloud.smart_ag_instance:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    smart_ag_name: branch-office-gw
    max_band_width: 50
"""

RETURN = r"""
smart_ag_instance:
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
        smart_ag_name=dict(type="str"),
        max_band_width=dict(type="int"),
        smart_ag_id=dict(type="str"),
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

    params = {}
    if module.params.get("smart_ag_name") is not None:
        params["SmartAgName"] = module.params["smart_ag_name"]
    if module.params.get("max_band_width") is not None:
        params["MaxBandWidth"] = module.params["max_band_width"]
    if module.params.get("smart_ag_id") is not None:
        params["SmartAgId"] = module.params["smart_ag_id"]

    try:
        result = client.get(
            "DescribeSmartAccessGateways",
            params,
            service_endpoint="smartag.aliyuncs.com",
            api_version="2018-03-13",
        )

        data = result
        for key in ["SmartAccessGateways", "SmartAccessGateway"]:
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateSmartAccessGateway",
                    params,
                    service_endpoint="smartag.aliyuncs.com",
                    api_version="2018-03-13",
                )
                changed = True
                module.exit_json(changed=changed, smart_ag_instance=result)
            else:
                module.exit_json(
                    changed=False,
                    smart_ag_instance=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteSmartAccessGateway",
                    params,
                    service_endpoint="smartag.aliyuncs.com",
                    api_version="2018-03-13",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
