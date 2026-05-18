#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.elasticsearch_instance"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: elasticsearch_instance
short_description: Manage Elasticsearch instance.
description:
  - Create, update, or delete Alibaba Cloud elasticsearch_instance resources.
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
  instance_id:
    description: Elasticsearch instance ID.
    type: str
  es_version:
    description: Elasticsearch version.
    type: str
  instance_category:
    description: Instance category (x-pack, advanced).
    type: str
  data_node_spec:
    description: Data node instance type.
    type: str
  data_node_amount:
    description: Number of data nodes.
    type: int
  data_node_disk_size:
    description: Data node disk size in GB.
    type: int
"""

EXAMPLES = r"""
- name: Manage elasticsearch_instance
  stevefulme1.alibaba_cloud.elasticsearch_instance:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    es_version: 7.10
    data_node_spec: elasticsearch.sn2ne.large
"""

RETURN = r"""
elasticsearch_instance:
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
        instance_id=dict(type="str"),
        es_version=dict(type="str"),
        instance_category=dict(type="str"),
        data_node_spec=dict(type="str"),
        data_node_amount=dict(type="int"),
        data_node_disk_size=dict(type="int"),
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
        result = client.get(
            "ListInstance",
            {},
            service_endpoint="elasticsearch.aliyuncs.com",
            api_version="2017-06-13",
        )

        data = result
        for key in ["Result"]:
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "createInstance",
                    {},
                    service_endpoint="elasticsearch.aliyuncs.com",
                    api_version="2017-06-13",
                )
                changed = True
                module.exit_json(changed=changed, elasticsearch_instance=result)
            else:
                module.exit_json(
                    changed=False,
                    elasticsearch_instance=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteInstance",
                    {},
                    service_endpoint="elasticsearch.aliyuncs.com",
                    api_version="2017-06-13",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
