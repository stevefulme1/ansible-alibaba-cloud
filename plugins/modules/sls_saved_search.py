#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sls_saved_search"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sls_saved_search
short_description: Manage saved search queries.
description:
  - Create, update, or delete Alibaba Cloud sls_saved_search resources.
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
  project_name:
    description: Log Service project name.
    type: str
  search_name:
    description: Saved search name.
    type: str
  search_query:
    description: SLS query expression.
    type: str
  logstore:
    description: Target logstore name.
    type: str
"""

EXAMPLES = r"""
- name: Manage sls_saved_search
  stevefulme1.alibaba_cloud.sls_saved_search:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    project_name: my-sls-project
    search_name: error-query
"""

RETURN = r"""
sls_saved_search:
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
        state=dict(
            type="str",
            choices=["present", "absent"],
            default="present",
        ),
        project_name=dict(type="str"),
        search_name=dict(type="str"),
        search_query=dict(type="str"),
        logstore=dict(type="str"),
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
    if module.params.get("project_name") is not None:
        params["ProjectName"] = module.params["project_name"]
    if module.params.get("search_name") is not None:
        params["SearchName"] = module.params["search_name"]
    if module.params.get("search_query") is not None:
        params["SearchQuery"] = module.params["search_query"]
    if module.params.get("logstore") is not None:
        params["Logstore"] = module.params["logstore"]


    try:
        result = client.get(
            "ListSavedSearch",
            params,
            service_endpoint="sls.aliyuncs.com",
            api_version="2020-12-30",
        )

        data = result
        for key in ["SavedSearches"]:
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateSavedSearch",
                    params,
                    service_endpoint="sls.aliyuncs.com",
                    api_version="2020-12-30",
                )
                changed = True
                module.exit_json(changed=changed, sls_saved_search=result)
            else:
                module.exit_json(
                    changed=False,
                    sls_saved_search=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteSavedSearch",
                    params,
                    service_endpoint="sls.aliyuncs.com",
                    api_version="2020-12-30",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
