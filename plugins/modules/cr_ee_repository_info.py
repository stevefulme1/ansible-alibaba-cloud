#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cr_ee_repository_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cr_ee_repository_info
short_description: Query Container Registry Enterprise Edition repositories.
description:
  - Retrieve information about Alibaba Cloud Container Registry EE repositories.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  instance_id:
    description: Container Registry EE instance ID.
    type: str
  repo_name:
    description: Filter by repository name.
    type: str
  repo_namespace_name:
    description: Filter by repository namespace name.
    type: str
"""

EXAMPLES = r"""
- name: Query all CR EE repositories
  stevefulme1.alibaba_cloud.cr_ee_repository_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: cri-123

- name: Query specific CR EE repository
  stevefulme1.alibaba_cloud.cr_ee_repository_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: cri-123
    repo_namespace_name: my-namespace
    repo_name: my-repo
"""

RETURN = r"""
cr_ee_repositories:
  description: List of Container Registry EE repositories.
  returned: success
  type: list
  elements: dict
  sample:
    - repo_id: repo-123
      repo_name: my-repo
      repo_namespace_name: my-namespace
      repo_type: PUBLIC
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
        repo_name=dict(type="str"),
        repo_namespace_name=dict(type="str"),
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
    if module.params.get("repo_name"):
        params["RepoName"] = module.params["repo_name"]
    if module.params.get("repo_namespace_name"):
        params["RepoNamespaceName"] = module.params["repo_namespace_name"]

    try:
        result = client.get(
            "ListRepository",
            params,
            service_endpoint="cr.aliyuncs.com",
            api_version="2018-12-01",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in ["Repositories"]:
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, cr_ee_repositories=data)


if __name__ == "__main__":
    main()
