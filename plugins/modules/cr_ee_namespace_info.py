#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cr_ee_namespace_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cr_ee_namespace_info
short_description: Query Container Registry Enterprise Edition namespaces.
description:
  - Retrieve information about Alibaba Cloud Container Registry EE namespaces.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  instance_id:
    description: Container Registry EE instance ID.
    type: str
  namespace_name:
    description: Filter by namespace name.
    type: str
"""

EXAMPLES = r"""
- name: Query all CR EE namespaces
  stevefulme1.alibaba_cloud.cr_ee_namespace_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: cri-123

- name: Query specific CR EE namespace
  stevefulme1.alibaba_cloud.cr_ee_namespace_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: cri-123
    namespace_name: my-namespace
"""

RETURN = r"""
cr_ee_namespaces:
  description: List of Container Registry EE namespaces.
  returned: success
  type: list
  elements: dict
  sample:
    - namespace_id: ns-123
      namespace_name: my-namespace
      auto_create_repo: false
      default_repo_type: PUBLIC
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
        namespace_name=dict(type="str"),
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
    if module.params.get("namespace_name"):
        params["NamespaceName"] = module.params["namespace_name"]

    try:
        result = client.get(
            "ListNamespace",
            params,
            service_endpoint="cr.aliyuncs.com",
            api_version="2018-12-01",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in ["Namespaces"]:
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, cr_ee_namespaces=data)


if __name__ == "__main__":
    main()
