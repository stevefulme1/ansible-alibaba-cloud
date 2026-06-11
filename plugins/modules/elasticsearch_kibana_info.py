#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.elasticsearch_kibana_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: elasticsearch_kibana_info
short_description: Query Elasticsearch Kibana configurations.
description:
  - Retrieve information about Alibaba Cloud Elasticsearch Kibana configurations.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  instance_id:
    description: Elasticsearch instance ID.
    type: str
    required: true
"""

EXAMPLES = r"""
- name: Query Elasticsearch Kibana configuration
  stevefulme1.alibaba_cloud.elasticsearch_kibana_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: es-123
"""

RETURN = r"""
elasticsearch_kibana:
  description: Kibana configuration details.
  returned: success
  type: dict
  sample:
    instance_id: es-123
    kibana_version: 7.10.0
    kibana_endpoint: https://es-123-kibana.public.elasticsearch.aliyuncs.com:5601
    kibana_spec: elasticsearch.n4.small
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        instance_id=dict(type="str", required=True),
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
        "InstanceId": module.params["instance_id"],
    }

    try:
        result = client.get(
            "DescribeKibanaSettings",
            params,
            service_endpoint="elasticsearch.aliyuncs.com",
            api_version="2017-06-13",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Extract Result data
    data = result.get("Result", {})

    module.exit_json(changed=False, elasticsearch_kibana=data)


if __name__ == "__main__":
    main()
