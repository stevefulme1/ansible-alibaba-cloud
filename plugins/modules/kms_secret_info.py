#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.kms_secret_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: kms_secret_info
short_description: Query KMS secrets.
description:
  - Retrieve information about Alibaba Cloud Key Management Service secrets.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  secret_name:
    description: Filter by secret name.
    type: str
"""

EXAMPLES = r"""
- name: Query all KMS secrets
  stevefulme1.alibaba_cloud.kms_secret_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific KMS secret
  stevefulme1.alibaba_cloud.kms_secret_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    secret_name: my-secret
"""

RETURN = r"""
kms_secrets:
  description: List of KMS secrets.
  returned: success
  type: list
  elements: dict
  sample:
    - secret_name: my-secret
      secret_type: Generic
      create_time: "2021-01-01T00:00:00Z"
      update_time: "2021-01-02T00:00:00Z"
      planned_delete_time: null
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        secret_name=dict(type="str"),
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
    if module.params.get("secret_name"):
        params["SecretName"] = module.params["secret_name"]

    try:
        result = client.get(
            "ListSecrets",
            params,
            service_endpoint="kms.aliyuncs.com",
            api_version="2016-01-20",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "SecretList.Secret".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, kms_secrets=data)


if __name__ == "__main__":
    main()
