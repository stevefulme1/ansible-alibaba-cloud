#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.acm_configuration_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: acm_configuration_info
short_description: Query ACM application configurations.
description:
  - Retrieve information about Alibaba Cloud ACM configuration resources.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  namespace_id:
    description: Configuration namespace ID.
    type: str
  data_id:
    description: Filter by configuration data ID.
    type: str
  group:
    description: Filter by configuration group.
    type: str
  limit:
    description:
      - Maximum number of results to return.
    type: int
    default: 100
  offset:
    description:
      - Number of results to skip for pagination.
    type: int
    default: 0
"""

EXAMPLES = r"""
- name: List all ACM configurations
  stevefulme1.alibaba_cloud.acm_configuration_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    namespace_id: example-value
    data_id: example-value
"""

RETURN = r"""
acm_configurations:
  description: List of ACM configurations.
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
        limit=dict(type="int", default=100),
        offset=dict(type="int", default=0),
        namespace_id=dict(type="str"),
        data_id=dict(type="str"),
        group=dict(type="str"),
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
    try:
        result = client.get(
            "GetConfig",
            params,
            service_endpoint="acm.aliyuncs.com",
            api_version="2020-02-06",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    data = result
    for key in "Configurations.Configuration".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, acm_configurations=data)


if __name__ == "__main__":
    main()
