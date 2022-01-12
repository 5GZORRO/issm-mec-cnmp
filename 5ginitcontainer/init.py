# Copyright 2021 - 2022 IBM Corporation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import time

import kubernetes
from kubernetes.client.rest import ApiException

from kubernetes.client import V1ObjectMeta

from kubernetes.client import V1Service
from kubernetes.client import V1ServiceSpec
from kubernetes.client import V1ServicePort

from kubernetes.client import V1Endpoints
from kubernetes.client import V1EndpointSubset
from kubernetes.client import V1EndpointAddress
from kubernetes.client import V1EndpointPort

from kubernetes.client import V1OwnerReference


CR_NAME = os.getenv('CR_NAME')
DIR = os.getenv('DIR')
FILE = os.getenv('FILE')
CR_KIND = os.getenv('CR_KIND')
CR_UID = os.getenv('CR_UID')


SEC_WAIT = 1


def generate_owner_reference(cr_kind, cr_name, cr_uid):
    """
    Creates OwnerReference object for the managing CR. OwnerReference is set in
    all objects created by this init-container. These will be automatically
    garbage collected once the CR is removed.

    :param cr_kind: the kind of the CR
    :type cr_kind: ``str``

    :param cr_name: the name of the CR
    :type cr_name: ``str``

    :param cr_uid: the uid of the CR
    :type cr_uid: ``str``
    """
    return V1OwnerReference(
        api_version='5g.ibm.com/v1alpha1',
        block_owner_deletion=True, controller=True, kind=cr_kind,
        name=cr_name, 
        uid=cr_uid)


def generate_service_endpoint(cr_name, network_name, ipaddress):
    """
    Generates service and endpoint objects with the given parameters
    """

    print ('[TRACE] enter generate_service_endpoint')
    service_object_meta = V1ObjectMeta(
        name='%s-%s' % (cr_name, network_name),
        owner_references=[generate_owner_reference(cr_kind=CR_KIND,
                                                   cr_name=cr_name,
                                                   cr_uid=CR_UID)])

    # Note: port 80 not actually being used
    service_port = V1ServicePort(port=80, protocol='TCP')
    service_spec = V1ServiceSpec(cluster_ip="None", ports=[service_port])

    ep_address = V1EndpointAddress(ip=ipaddress)
    ep_subset = V1EndpointSubset(addresses=[ep_address], ports=[V1EndpointPort(port=80)])

    print ('[TRACE] exit generate_service_endpoint')
    return V1Service(metadata=service_object_meta, spec=service_spec), \
        V1Endpoints(metadata=service_object_meta, subsets=[ep_subset]),


def main():
    print ('[TRACE] enter main()')
    print ('*** CR_NAME %s' % CR_NAME)
    print ('*** CR_KIND %s' % CR_KIND)
    print ('*** CR_UID %s' % CR_UID)
    print ('*** DIR %s' % DIR)
    print ('*** FILE %s' % FILE)

    if not CR_NAME or not CR_KIND or not CR_UID or not DIR or not FILE:
        raise Exception('[ERROR] One or more environment variables is missing '
                        'with an actual value.')

    kubernetes.config.load_incluster_config()
    print ('[DEBUG] successfully configured in_cluster config')
    core_api = kubernetes.client.CoreV1Api()

    network_status = None
    while True:
        with open(os.path.join(DIR, FILE), 'r') as f:
            for l in f.readlines():
                print ('[DEBUG] [%s]: reading line: %s' % (FILE, l))
                if l.startswith('k8s.v1.cni.cncf.io/network-status'):
                    network_status = l.split('k8s.v1.cni.cncf.io/network-status=')[1]
                    break

            # it might be that status is not available yet..
            if not network_status:
                print ('[DEBUG] unable to find network-status. waiting..')
                time.sleep(SEC_WAIT)
            else:
                break

    values = json.loads(network_status)
    print ('[INFO] network_status values: %s' % values)
    for v in json.loads(values):
        print ('single network: %s' % v)
        if v['name']:
            try:
                namespace = v['name'].split('/')[0]
                network_name = v['name'].split('/')[1]
                ip = v['ips'][0]
            except Exception as e:
                print ('[WARN] single network not in desired format. "%s". Ignoring' %
                       str(e))
                continue
            print ('[INFO] preparing service/endpoint for %s with ipaddress: %s' %
                    (network_name, ip))
            service, endpoint = generate_service_endpoint(CR_NAME, network_name, ip)

            try:
                print ('[INFO] create service %s ...' % network_name)
                core_api.create_namespaced_service(
                    namespace=namespace, body=service)
            except ApiException as e:
                print ('[WARN] create_namespaced_service failed: %s' % str(e))
                if e.status != 409:
                    raise

            try:
                print ('[INFO] create endpoint for %s with ip: %s ...' %
                        (network_name, ip))
                core_api.create_namespaced_endpoints(
                    namespace=namespace, body=endpoint)
            except ApiException as e:
                print ('[WARN] create_namespaced_endpoints failed: %s' % str(e))
                if e.status != 409:
                    raise
        else:
            print ('[WARN] single network with no name. Ignoring')

    print ('[TRACE] exit main()')

if __name__ == '__main__':
    main()
