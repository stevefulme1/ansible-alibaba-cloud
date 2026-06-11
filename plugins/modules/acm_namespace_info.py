#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.acm_namespace_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: acm_namespace_info
short_description: Query ACM configuration namespaces.
description:
  - Retrieve information about Alibaba Cloud ACM configuration namespaces.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  namespace_id:
    description: Filter by namespace ID.
    type: str
"""

EXAMPLES = r"""
- name: Query ACM namespaces
  stevefulme1.alibaba_cloud.acm_namespace_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific ACM namespace by ID
  stevefulme1.alibaba_cloud.acm_namespace_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    namespace_id: example-namespace-id
"""

RETURN = r"""
acm_namespaces:
  description: List of ACM namespaces.
  returned: success
  type: list
  elements: dict
  sample:
    - namespace_id: example-id
      namespace_name: example-name
      namespace_desc: example description
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        namespace_id=dict(type="str"),
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
    if module.params.get("namespace_id"):
        params["NamespaceId"] = module.params["namespace_id"]

    try:
        result = client.get(
            "DescribeNamespace",
            params,
            service_endpoint="acm.aliyuncs.com",
            api_version="2020-02-06",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Namespaces.Namespace".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, acm_namespaces=data)


if __name__ == "__main__":
    main()
