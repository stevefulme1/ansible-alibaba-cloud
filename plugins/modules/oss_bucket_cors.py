#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.oss_bucket_cors"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: oss_bucket_cors
short_description: Manage OSS bucket CORS rules.
description:
  - Configure CORS rules for an Alibaba Cloud OSS bucket.
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
  bucket_name:
    description: Name of the OSS bucket.
    type: str
  allowed_origins:
    description: Allowed CORS origins.
    type: list
    elements: str
  allowed_methods:
    description: Allowed HTTP methods.
    type: list
    elements: str
  allowed_headers:
    description: Allowed request headers.
    type: list
    elements: str
"""

EXAMPLES = r"""
- name: Manage OSS bucket CORS rules
  stevefulme1.alibaba_cloud.oss_bucket_cors:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
oss_bucket_cors:
  description: Resource details.
  returned: success
  type: dict
"""

import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        state=dict(type="str", choices=["present", "absent"], default="present"),
        bucket_name=dict(type="str"),
        allowed_origins=dict(type="list", elements="str"),
        allowed_methods=dict(type="list", elements="str"),
        allowed_headers=dict(type="list", elements="str"),
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
    if module.params.get("bucket_name") is not None:
        params["BucketName"] = module.params["bucket_name"]
    if module.params.get("allowed_origins") is not None:
        params["AllowedOrigins"] = json.dumps(module.params["allowed_origins"])
    if module.params.get("allowed_methods") is not None:
        params["AllowedMethods"] = json.dumps(module.params["allowed_methods"])
    if module.params.get("allowed_headers") is not None:
        params["AllowedHeaders"] = json.dumps(module.params["allowed_headers"])

    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "GetBucketCors",
            params,
            service_endpoint="oss.aliyuncs.com",
            api_version="2019-05-17",
        )

        data = existing
        for key in "CORSConfiguration".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "PutBucketCors",
                    params,
                    service_endpoint="oss.aliyuncs.com",
                    api_version="2019-05-17",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    oss_bucket_cors=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    oss_bucket_cors=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteBucketCors",
                    params,
                    service_endpoint="oss.aliyuncs.com",
                    api_version="2019-05-17",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
