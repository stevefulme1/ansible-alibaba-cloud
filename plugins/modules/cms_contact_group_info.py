#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cms_contact_group_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cms_contact_group_info
short_description: Query Cloud Monitor alert contact groups.
description:
  - Retrieve information about Alibaba Cloud Monitor alert contact groups.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  contact_group_name:
    description: Filter by contact group name.
    type: str
"""

EXAMPLES = r"""
- name: Query all Cloud Monitor alert contact groups
  stevefulme1.alibaba_cloud.cms_contact_group_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific alert contact group
  stevefulme1.alibaba_cloud.cms_contact_group_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    contact_group_name: oncall-group
"""

RETURN = r"""
cms_contact_groups:
  description: List of Cloud Monitor alert contact groups.
  returned: success
  type: list
  elements: dict
  sample:
    - contact_group_name: oncall-group
      describe: On-call rotation group
      contacts:
        - user1
        - user2
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        contact_group_name=dict(type="str"),
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
    if module.params.get("contact_group_name"):
        params["ContactGroupName"] = module.params["contact_group_name"]

    try:
        result = client.get(
            "DescribeContactGroupList",
            params,
            service_endpoint="metrics.aliyuncs.com",
            api_version="2019-01-01",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "ContactGroupList.ContactGroup".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, cms_contact_groups=data)


if __name__ == "__main__":
    main()
