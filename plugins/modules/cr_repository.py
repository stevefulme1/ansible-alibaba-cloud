#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cr_repository"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cr_repository
short_description: Manage Container Registry repositories.
description:
  - Create or delete Alibaba Cloud Container Registry repositories.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  state:
    description: Desired state of the resource.
    type: str
    choices: ['present', 'absent']
    default: present
  instance_id:
    description: Container Registry instance ID.
    type: str
  repo_name:
    description: Repository name.
    type: str
  repo_namespace_name:
    description: Namespace for the repository.
    type: str
  repo_type:
    description: Repository visibility.
    type: str
    choices: ['PUBLIC', 'PRIVATE']
  summary:
    description: Repository summary.
    type: str
"""

EXAMPLES = r"""
- name: Manage Container Registry repositories
  stevefulme1.alibaba_cloud.cr_repository:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
cr_repository:
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
        state=dict(type="str", choices=["present", "absent"], default="present"),
        instance_id=dict(type="str"),
        repo_name=dict(type="str"),
        repo_namespace_name=dict(type="str"),
        repo_type=dict(type="str", choices=["PUBLIC", "PRIVATE"]),
        summary=dict(type="str"),
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

    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "ListRepository",
            {},
            service_endpoint="cr.aliyuncs.com",
            api_version="2018-12-01",
        )

        data = existing
        for key in "Repositories".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateRepository",
                    {},
                    service_endpoint="cr.aliyuncs.com",
                    api_version="2018-12-01",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    cr_repository=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    cr_repository=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteRepository",
                    {},
                    service_endpoint="cr.aliyuncs.com",
                    api_version="2018-12-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
