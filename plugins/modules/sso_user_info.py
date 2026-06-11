#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sso_user_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sso_user_info
short_description: Query CloudSSO users.
description:
  - Retrieve information about Alibaba Cloud CloudSSO users.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  directory_id:
    description: CloudSSO directory ID.
    type: str
    required: true
  user_name:
    description: Filter by user name.
    type: str
"""

EXAMPLES = r"""
- name: Query all CloudSSO users
  stevefulme1.alibaba_cloud.sso_user_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    directory_id: d-xxxxx

- name: Query specific CloudSSO user
  stevefulme1.alibaba_cloud.sso_user_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    directory_id: d-xxxxx
    user_name: jdoe
"""

RETURN = r"""
sso_users:
  description: List of CloudSSO users.
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
        directory_id=dict(type="str", required=True),
        user_name=dict(type="str"),
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
        "DirectoryId": module.params["directory_id"],
    }
    if module.params.get("user_name"):
        params["UserName"] = module.params["user_name"]

    try:
        result = client.get(
            "ListUsers",
            params,
            service_endpoint="cloudsso.aliyuncs.com",
            api_version="2021-05-15",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Users".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, sso_users=data)


if __name__ == "__main__":
    main()
