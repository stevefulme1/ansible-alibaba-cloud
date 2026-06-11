#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.directmail_sender_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: directmail_sender_info
short_description: Query DirectMail sender addresses.
description:
  - Retrieve information about Alibaba Cloud DirectMail sender addresses.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  sender_id:
    description: Filter by sender ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all DirectMail sender addresses
  stevefulme1.alibaba_cloud.directmail_sender_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific DirectMail sender address
  stevefulme1.alibaba_cloud.directmail_sender_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    sender_id: "123456"
"""

RETURN = r"""
directmail_senders:
  description: List of DirectMail sender addresses.
  returned: success
  type: list
  elements: dict
  sample:
    - sender_id: "123456"
      account_name: noreply@example.com
      reply_address: support@example.com
      sender_status: 1
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        sender_id=dict(type="str"),
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
    if module.params.get("sender_id"):
        params["SenderId"] = module.params["sender_id"]

    try:
        result = client.get(
            "QuerySenderAddressList",
            params,
            service_endpoint="dm.aliyuncs.com",
            api_version="2015-11-23",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in ["MailAddressList", "MailAddress"]:
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, directmail_senders=data)


if __name__ == "__main__":
    main()
