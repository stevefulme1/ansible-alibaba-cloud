#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sls_saved_search_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sls_saved_search_info
short_description: Query SLS saved searches.
description:
  - Retrieve information about Alibaba Cloud Log Service saved searches.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  project_name:
    description: Log Service project name.
    type: str
    required: true
  search_name:
    description: Filter by saved search name.
    type: str
"""

EXAMPLES = r"""
- name: Query all saved searches
  stevefulme1.alibaba_cloud.sls_saved_search_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    project_name: my-sls-project

- name: Query specific saved search
  stevefulme1.alibaba_cloud.sls_saved_search_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    project_name: my-sls-project
    search_name: error-query
"""

RETURN = r"""
sls_saved_searches:
  description: List of SLS saved searches.
  returned: success
  type: list
  elements: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        project_name=dict(type="str", required=True),
        search_name=dict(type="str"),
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

    params = {
        "ProjectName": module.params["project_name"],
    }
    if module.params.get("search_name"):
        params["SearchName"] = module.params["search_name"]

    try:
        result = client.get(
            "ListSavedSearch",
            params,
            service_endpoint="sls.aliyuncs.com",
            api_version="2020-12-30",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in ["SavedSearches"]:
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, sls_saved_searches=data)


if __name__ == "__main__":
    main()
