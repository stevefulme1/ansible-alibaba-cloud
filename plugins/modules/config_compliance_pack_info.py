#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.config_compliance_pack_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: config_compliance_pack_info
short_description: Query Cloud Config compliance packs.
description:
  - Retrieve information about Alibaba Cloud Config compliance packs.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  compliance_pack_id:
    description: Filter by compliance pack ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all compliance packs
  stevefulme1.alibaba_cloud.config_compliance_pack_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific compliance pack
  stevefulme1.alibaba_cloud.config_compliance_pack_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    compliance_pack_id: cp-123
"""

RETURN = r"""
config_compliance_packs:
  description: List of Cloud Config compliance packs.
  returned: success
  type: list
  elements: dict
  sample:
    - compliance_pack_id: cp-123
      compliance_pack_name: CIS Benchmark
      status: ACTIVE
      risk_level: 1
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        compliance_pack_id=dict(type="str"),
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
    if module.params.get("compliance_pack_id"):
        params["CompliancePackId"] = module.params["compliance_pack_id"]

    try:
        result = client.get(
            "ListCompliancePacks",
            params,
            service_endpoint="config.aliyuncs.com",
            api_version="2020-09-07",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "CompliancePacksResult.CompliancePacks".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, config_compliance_packs=data)


if __name__ == "__main__":
    main()
