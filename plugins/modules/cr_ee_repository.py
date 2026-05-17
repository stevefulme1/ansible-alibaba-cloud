#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cr_ee_repository"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cr_ee_repository
short_description: Manage Container Registry EE repository.
description:
  - Create, update, or delete Alibaba Cloud cr_ee_repository resources.
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
  instance_id:
    description: EE instance ID.
    type: str
  namespace_name:
    description: Namespace name.
    type: str
  repo_name:
    description: Repository name.
    type: str
  repo_type:
    description: Repository visibility (PUBLIC, PRIVATE).
    type: str
"""

EXAMPLES = r"""
- name: Manage cr_ee_repository
  stevefulme1.alibaba_cloud.cr_ee_repository:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    instance_id: cri-xxx
    repo_name: myapp
"""

RETURN = r"""
cr_ee_repository:
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
        instance_id=dict(type="str"),
        namespace_name=dict(type="str"),
        repo_name=dict(type="str"),
        repo_type=dict(type="str"),
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
    if module.params.get("instance_id") is not None:
        params["InstanceId"] = module.params["instance_id"]
    if module.params.get("namespace_name") is not None:
        params["NamespaceName"] = module.params["namespace_name"]
    if module.params.get("repo_name") is not None:
        params["RepoName"] = module.params["repo_name"]
    if module.params.get("repo_type") is not None:
        params["RepoType"] = module.params["repo_type"]


    try:
        result = client.get(
            "ListRepository",
            params,
            service_endpoint="cr.aliyuncs.com",
            api_version="2018-12-01",
        )

        data = result
        for key in ["Repositories"]:
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateRepository",
                    params,
                    service_endpoint="cr.aliyuncs.com",
                    api_version="2018-12-01",
                )
                changed = True
                module.exit_json(changed=changed, cr_ee_repository=result)
            else:
                module.exit_json(
                    changed=False,
                    cr_ee_repository=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteRepository",
                    params,
                    service_endpoint="cr.aliyuncs.com",
                    api_version="2018-12-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
