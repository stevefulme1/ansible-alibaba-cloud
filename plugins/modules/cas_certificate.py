#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cas_certificate"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cas_certificate
short_description: Manage SSL certificates.
description:
  - Upload or delete SSL certificates in Alibaba Cloud CAS.
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
  certificate_id:
    description: Certificate ID for deletion.
    type: int
  name:
    description: Certificate name.
    type: str
  cert:
    description: PEM-encoded certificate body.
    type: str
  certificate_key:
    description: PEM-encoded private key.
    type: str
"""

EXAMPLES = r"""
- name: Manage SSL certificates
  stevefulme1.alibaba_cloud.cas_certificate:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
cas_certificate:
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
        certificate_id=dict(type="int"),
        name=dict(type="str"),
        cert=dict(type="str"),
        certificate_key=dict(type="str", no_log=True),
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
    if module.params.get("certificate_id") is not None:
        params["CertificateId"] = module.params["certificate_id"]
    if module.params.get("name") is not None:
        params["Name"] = module.params["name"]
    if module.params.get("cert") is not None:
        params["Cert"] = module.params["cert"]
    if module.params.get("certificate_key") is not None:
        params["CertificateKey"] = module.params["certificate_key"]


    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "ListUserCertificateOrder",
            params,
            service_endpoint="cas.aliyuncs.com",
            api_version="2020-04-07",
        )

        data = existing
        for key in "CertificateOrderList".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "UploadUserCertificate",
                    params,
                    service_endpoint="cas.aliyuncs.com",
                    api_version="2020-04-07",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    cas_certificate=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    cas_certificate=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteUserCertificate",
                    params,
                    service_endpoint="cas.aliyuncs.com",
                    api_version="2020-04-07",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
