#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dataworks_folder_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: dataworks_folder_info
short_description: Query DataWorks folders.
description:
  - Retrieve information about Alibaba Cloud DataWorks folders.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  project_id:
    description: DataWorks project ID.
    type: str
  folder_id:
    description: Filter by folder ID.
    type: str
  folder_path:
    description: Filter by folder path.
    type: str
"""

EXAMPLES = r"""
- name: Query all DataWorks folders
  stevefulme1.alibaba_cloud.dataworks_folder_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    project_id: "12345"

- name: Query specific DataWorks folder
  stevefulme1.alibaba_cloud.dataworks_folder_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    project_id: "12345"
    folder_id: "67890"
"""

RETURN = r"""
dataworks_folders:
  description: List of DataWorks folders.
  returned: success
  type: list
  elements: dict
  sample:
    - folder_id: "67890"
      folder_name: etl_scripts
      folder_path: /Business Flow/etl_scripts
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
        folder_id=dict(type="str"),
        folder_path=dict(type="str"),
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
    if module.params.get("folder_id"):
        params["FolderId"] = module.params["folder_id"]
    if module.params.get("folder_path"):
        params["FolderPath"] = module.params["folder_path"]

    try:
        result = client.get(
            "ListFolders",
            params,
            service_endpoint="dataworks.{region_id}.aliyuncs.com",
            api_version="2020-05-18",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Folders.Folder".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, dataworks_folders=data)


if __name__ == "__main__":
    main()
