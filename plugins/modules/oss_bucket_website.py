#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.oss_bucket_website"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: oss_bucket_website
short_description: Manage OSS bucket static website hosting.
description:
  - Configure static website hosting for an Alibaba Cloud OSS bucket.
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
  index_document:
    description: Index document suffix.
    type: str
  error_document:
    description: Error document key.
    type: str
"""

EXAMPLES = r"""
- name: Manage OSS bucket static website hosting
  stevefulme1.alibaba_cloud.oss_bucket_website:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
oss_bucket_website:
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
        bucket_name=dict(type="str"),
        index_document=dict(type="str"),
        error_document=dict(type="str"),
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
    if module.params.get("index_document") is not None:
        params["IndexDocument"] = module.params["index_document"]
    if module.params.get("error_document") is not None:
        params["ErrorDocument"] = module.params["error_document"]

    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "GetBucketWebsite",
            params,
            service_endpoint="oss.aliyuncs.com",
            api_version="2019-05-17",
        )

        data = existing
        for key in "WebsiteConfiguration".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "PutBucketWebsite",
                    params,
                    service_endpoint="oss.aliyuncs.com",
                    api_version="2019-05-17",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    oss_bucket_website=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    oss_bucket_website=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteBucketWebsite",
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
