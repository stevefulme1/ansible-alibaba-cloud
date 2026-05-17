#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.kms_secret"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: kms_secret
short_description: Manage KMS secrets.
description:
  - Create, update, or delete Alibaba Cloud kms_secret resources.
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
  secret_name:
    description: Name of the secret.
    type: str
    required: true
  secret_data:
    description: Secret value to store.
    type: str
  version_id:
    description: Version identifier for the secret.
    type: str
"""

EXAMPLES = r"""
- name: Create KMS secret
  stevefulme1.alibaba_cloud.kms_secret:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    secret_name: db-password
    secret_data: "s3cret!"
    version_id: v1
"""

RETURN = r"""
secret:
  description: KMS secret metadata.
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
        secret_name=dict(type="str", required=True),
        secret_data=dict(type="str", no_log=True),
        version_id=dict(type="str"),
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
    if module.params.get("secret_name") is not None:
        params["SecretName"] = module.params["secret_name"]
    if module.params.get("secret_data") is not None:
        params["SecretData"] = module.params["secret_data"]
    if module.params.get("version_id") is not None:
        params["VersionId"] = module.params["version_id"]

    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "ListSecrets",
            params,
            service_endpoint="kms.aliyuncs.com",
            api_version="2016-01-20",
        )

        data = existing
        for key in "SecretList.Secret".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateSecret",
                    params,
                    service_endpoint="kms.aliyuncs.com",
                    api_version="2016-01-20",
                )
                changed = True
                module.exit_json(changed=changed, kms_secret=result)
            else:
                module.exit_json(
                    changed=False,
                    kms_secret=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteSecret",
                    params,
                    service_endpoint="kms.aliyuncs.com",
                    api_version="2016-01-20",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
