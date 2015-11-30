# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Vultr Driver
"""

import time
import base64

from libcloud.utils.py3 import httplib
from libcloud.utils.py3 import urlencode

from libcloud.common.base import ConnectionKey, JsonResponse
from libcloud.compute.types import Provider, NodeState
from libcloud.common.types import LibcloudError, InvalidCredsError
from libcloud.compute.base import NodeDriver
from libcloud.compute.base import Node, NodeImage, NodeSize, NodeLocation


class SSHKey(object):
    def __init__(self, id, name, ssh_key):
        self.id = id
        self.name = name
        self.ssh_key = ssh_key

    def __repr__(self):
        return (('<SSHKey: id=%s, name=%s, ssh_key=%s>') %
                (self.id, self.name, self.ssh_key))


class VultrResponse(JsonResponse):
    def parse_error(self):
        if self.status == httplib.OK:
            body = self.parse_body()
            return body
        elif self.status == httplib.FORBIDDEN:
            raise InvalidCredsError(self.body)
        else:
            raise LibcloudError(self.body)


class VultrConnection(ConnectionKey):
    """
    Connection class for the Vultr driver.
    """

    host = 'api.vultr.com'
    responseCls = VultrResponse

    def add_default_params(self, params):
        """
        Add parameters that are necessary for every request

        This method add ``api_key`` to
        the request.
        """
        params['api_key'] = self.key
        return params

    def encode_data(self, data):
        return urlencode(data)

    def get(self, url):
        return self.request(url)

    def post(self, url, data):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return self.request(url, data=data, headers=headers, method='POST')


class VultrNodeDriver(NodeDriver):
    """
    VultrNode node driver.
    """

    connectionCls = VultrConnection

    type = Provider.VULTR
    name = 'Vultr'
    website = 'https://www.vultr.com'

    NODE_STATE_MAP = {'pending': NodeState.PENDING,
                      'active': NodeState.RUNNING}

    def list_nodes(self):
        return self._list_resources('/v1/server/list', self._to_node)

    def list_locations(self):
        locations = self._list_resources('/v1/regions/list', self._to_location)
        return sorted(locations, key=lambda k: k.name)

    def list_sizes(self):
        sizes = self._list_resources('/v1/plans/list', self._to_size)
        return sorted(sizes, key=lambda k: float(k.price.replace('/month', '')))

    def list_images(self):
        images = self._list_resources('/v1/os/list', self._to_image)
        return sorted(images, key=lambda k: k.name)

    def create_node(self, name, size, image, location, ssh_key=[], userdata=None):

        # SSHKEYID string (optional) List of SSH keys to apply to this server
        # on install (only valid for Linux/FreeBSD).  See v1/sshkey/list.
        # Seperate keys with commas

        params = {'DCID': location.id, 'VPSPLANID': size.id,
                  'OSID': image.id, 'label': name}
        if ssh_key:
            params['SSHKEYID'] = ','.join(ssh_key)

        if userdata:
            userdata = base64.b64encode(userdata).decode('ascii')
            params['userdata'] = userdata

        result = self.connection.post('/v1/server/create', params)
        if result.status != httplib.OK:
            return False

        subid = result.object['SUBID']

        retry_count = 3
        created_node = None

        for i in range(retry_count):
            try:
                nodes = self.list_nodes()
                created_node = [n for n in nodes if n.id == subid][0]
            except IndexError:
                time.sleep(1)
                pass
            else:
                break

        return created_node

    def ex_stop_node(self, node):
        params = {'SUBID': node.id}
        res = self.connection.post('/v1/server/halt', params)

        return res.status == httplib.OK

    def ex_start_node(self, node):
        params = {'SUBID': node.id}
        res = self.connection.post('/v1/server/start', params)

        return res.status == httplib.OK

    def reboot_node(self, node):
        params = {'SUBID': node.id}
        res = self.connection.post('/v1/server/reboot', params)

        return res.status == httplib.OK

    def reboot_node(self, node):
        params = {'SUBID': node.id}
        res = self.connection.post('/v1/server/reboot', params)

        return res.status == httplib.OK

    def destroy_node(self, node):
        params = {'SUBID': node.id}
        res = self.connection.post('/v1/server/destroy', params)

        return res.status == httplib.OK

    def ex_list_ssh_keys(self):
        """
        List all the available SSH keys.

        :return: Available SSH keys.
        :rtype: ``list`` of :class:`SSHKey`
        """
        data = self.connection.request(' /v1/sshkey/list').object
        return list(map(self._to_ssh_key, data.values()))

    def ex_create_ssh_key(self, name, ssh_key):
        """
        Create a new SSH key.

        :param      name: Key name (required)
        :type       name: ``str``

        :param      name: Valid public key string (required)
        :type       name: ``str``
        """
        params = {'name': name, 'ssh_key': ssh_key}
        data = self.connection.post('/v1/sshkey/create', params).object
        return SSHKey(id=data.get('SSHKEYID'), name=name,
                      ssh_key=ssh_key)

    def _list_resources(self, url, tranform_func):
        data = self.connection.get(url).object
        sorted_key = sorted(data)
        return [tranform_func(data[key]) for key in sorted_key]

    def _to_node(self, data):
        if 'status' in data:
            state = self.NODE_STATE_MAP.get(data['status'], NodeState.UNKNOWN)
            if state == NodeState.RUNNING and \
               data['power_status'] != 'running':
                state = NodeState.STOPPED
        else:
            state = NodeState.UNKNOWN
        if 'main_ip' in data and data['main_ip'] not in [0, '', None]:
            public_ips = [data['main_ip']]
        else:
            public_ips = []

        extra_keys = ['os', 'kvm_url', 'date_created',
                      'pending_charges', 'cost_per_month', 'location',
                      'vcpu_count', 'disk', 'allowed_bandwidth_gb', 'ram',
                      'default_password']

        extra = {}
        for key in extra_keys:
            if key in data:
                extra[key] = data[key]

        node = Node(id=data['SUBID'], name=data['label'], state=state,
                    public_ips=public_ips, private_ips=None, extra=extra,
                    driver=self)

        return node

    def _to_location(self, data):
        return NodeLocation(id=data['DCID'], name=data['name'],
                            country=data['country'], driver=self)

    def _to_size(self, data):
        extra = {'vcpu_count': int(data['vcpu_count'])}
        ram = int(data['ram'])
        disk = int(data['disk'])
        bandwidth = float(data['bandwidth'])
        price = "%s/month" % data['price_per_month']

        return NodeSize(id=data['VPSPLANID'], name=data['name'],
                        ram=ram, disk=disk,
                        bandwidth=bandwidth, price=price,
                        extra=extra, driver=self)

    def _to_image(self, data):
        extra = {'arch': data['arch'], 'family': data['family']}
        return NodeImage(id=data['OSID'], name=data['name'], extra=extra,
                         driver=self)

    def _to_ssh_key(self, data):
        return SSHKey(id=data.get('SSHKEYID'), name=data.get('name'),
                      ssh_key=data.get('ssh_key', None))
