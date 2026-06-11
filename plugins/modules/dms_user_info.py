#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dms_user_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: dms_user_info
short_description: Query DMS users.
description:
  - Retrieve information about Alibaba Cloud DMS (Data Management Service) users.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  user_id:
    description: Filter by user ID.
    type: str
  user_name:
    description: Filter by user name.
    type: str
"""

EXAMPLES = r"""
- name: Query all DMS users
  stevefulme1.alibaba_cloud.dms_user_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific DMS user
  stevefulme1.alibaba_cloud.dms_user_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    user_id: "123456"
"""

RETURN = r"""
dms_users:
  description: List of DMS users.
  returned: success
  type: list
  elements: dict
  sample:
    - user_id: "123456"
      user_name: dbadmin
      nick_name: Database Administrator
      role_names: DBA
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        user_id=dict(type="str"),
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

    params = {}
    if module.params.get("user_id"):
        params["UserId"] = module.params["user_id"]
    if module.params.get("user_name"):
        params["UserName"] = module.params["user_name"]

    try:
        result = client.get(
            "ListUsers",
            params,
            service_endpoint="dms-enterprise.aliyuncs.com",
            api_version="2018-11-01",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Users.User".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, dms_users=data)


if __name__ == "__main__":
    main()
