#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cr_repository_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cr_repository_info
short_description: Query Container Registry repositories.
description:
  - Retrieve information about Alibaba Cloud Container Registry repositories.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  repo_name:
    description: Filter by repository name.
    type: str
  repo_namespace:
    description: Filter by repository namespace.
    type: str
"""

EXAMPLES = r"""
- name: Query all CR repositories
  stevefulme1.alibaba_cloud.cr_repository_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific CR repository
  stevefulme1.alibaba_cloud.cr_repository_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    repo_namespace: my-namespace
    repo_name: my-repo
"""

RETURN = r"""
cr_repositories:
  description: List of Container Registry repositories.
  returned: success
  type: list
  elements: dict
  sample:
    - repo_name: my-repo
      repo_namespace: my-namespace
      repo_type: PUBLIC
      summary: My container repository
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        repo_name=dict(type="str"),
        repo_namespace=dict(type="str"),
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
    if module.params.get("repo_name"):
        params["RepoName"] = module.params["repo_name"]
    if module.params.get("repo_namespace"):
        params["RepoNamespace"] = module.params["repo_namespace"]

    try:
        result = client.get(
            "GetRepoList",
            params,
            service_endpoint="cr.aliyuncs.com",
            api_version="2018-12-01",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Repositories".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, cr_repositories=data)


if __name__ == "__main__":
    main()
