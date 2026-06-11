#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.fc_alias_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: fc_alias_info
short_description: Query Function Compute service aliases.
description:
  - Retrieve information about Alibaba Cloud Function Compute service aliases.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  service_name:
    description: Function Compute service name.
    type: str
    required: true
  alias_name:
    description: Filter by alias name.
    type: str
"""

EXAMPLES = r"""
- name: Query all FC service aliases
  stevefulme1.alibaba_cloud.fc_alias_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    service_name: my-service

- name: Query specific FC service alias
  stevefulme1.alibaba_cloud.fc_alias_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    service_name: my-service
    alias_name: LATEST
"""

RETURN = r"""
fc_aliases:
  description: List of Function Compute service aliases.
  returned: success
  type: list
  elements: dict
  sample:
    - alias_name: LATEST
      version_id: "1"
      description: Latest version
      additional_version_weight:
        "2": 0.1
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        service_name=dict(type="str", required=True),
        alias_name=dict(type="str"),
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
        "ServiceName": module.params["service_name"],
    }
    if module.params.get("alias_name"):
        params["AliasName"] = module.params["alias_name"]

    try:
        result = client.get(
            "ListAliases",
            params,
            service_endpoint="fc.aliyuncs.com",
            api_version="2016-08-15",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in ["aliases"]:
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, fc_aliases=data)


if __name__ == "__main__":
    main()
