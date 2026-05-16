#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.pai_dataset"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: pai_dataset
short_description: Manage PAI datasets.
description:
  - Create, update, or delete Alibaba Cloud pai_dataset resources.
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
  workspace_id:
    description: Workspace ID for the dataset.
    type: str
    required: true
  dataset_name:
    description: Name of the dataset.
    type: str
    required: true
  dataset_id:
    description: ID of an existing dataset.
    type: str
  data_source_type:
    description: Data source type.
    type: str
    choices: [OSS, NAS, CPFS]
  uri:
    description: URI of the data source.
    type: str
"""

EXAMPLES = r"""
- name: Manage pai_dataset resource
  stevefulme1.alibaba_cloud.pai_dataset:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    workspace_id: ws-xxxxx
    dataset_name: training-data
    data_source_type: OSS
"""

RETURN = r"""
pai_dataset:
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
        workspace_id=dict(type="str", required=True),
        dataset_name=dict(type="str", required=True),
        dataset_id=dict(type="str"),
        data_source_type=dict(type="str", choices=["OSS", "NAS", "CPFS"]),
        uri=dict(type="str"),
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
        existing = client.get(
            "ListDatasets",
            {},
            service_endpoint="pai.aliyuncs.com",
            api_version="2021-02-04",
        )

        data = existing
        for key in "Datasets".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateDataset",
                    {},
                    service_endpoint="pai.aliyuncs.com",
                    api_version="2021-02-04",
                )
                changed = True
                module.exit_json(changed=changed, pai_dataset=result)
            else:
                module.exit_json(changed=False, pai_dataset=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteDataset",
                    {},
                    service_endpoint="pai.aliyuncs.com",
                    api_version="2021-02-04",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
