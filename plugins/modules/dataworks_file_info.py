#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dataworks_file_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: dataworks_file_info
short_description: Query DataWorks files.
description:
  - Retrieve information about Alibaba Cloud DataWorks files.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  project_id:
    description: DataWorks project ID.
    type: str
  file_id:
    description: Filter by file ID.
    type: str
  file_name:
    description: Filter by file name.
    type: str
"""

EXAMPLES = r"""
- name: Query all DataWorks files
  stevefulme1.alibaba_cloud.dataworks_file_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    project_id: "12345"

- name: Query specific DataWorks file
  stevefulme1.alibaba_cloud.dataworks_file_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    project_id: "12345"
    file_id: "67890"
"""

RETURN = r"""
dataworks_files:
  description: List of DataWorks files.
  returned: success
  type: list
  elements: dict
  sample:
    - file_id: "67890"
      file_name: etl_job.py
      file_type: ODPS_PYTHON
      owner_id: "user123"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        project_id=dict(type="str"),
        file_id=dict(type="str"),
        file_name=dict(type="str"),
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
    if module.params.get("project_id"):
        params["ProjectId"] = module.params["project_id"]
    if module.params.get("file_id"):
        params["FileId"] = module.params["file_id"]
    if module.params.get("file_name"):
        params["FileName"] = module.params["file_name"]

    try:
        result = client.get(
            "ListFiles",
            params,
            service_endpoint="dataworks.{region_id}.aliyuncs.com",
            api_version="2020-05-18",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Files.File".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, dataworks_files=data)


if __name__ == "__main__":
    main()
