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

import flask
import json
import os
import requests
import sys
import yaml

from gevent.wsgi import WSGIServer
from werkzeug.exceptions import HTTPException

import kubernetes
from kubernetes.client import V1Namespace
from kubernetes.client import V1ObjectMeta
from kubernetes.client.rest import ApiException


registry_private_free5gc = os.getenv('REGISTRY_PRIVATE_FREE5GC')
print ('**registry_private_free5gc: %s**' % registry_private_free5gc)

KAFKA_HOST = os.getenv('KAFKA_HOST')
print ('**kafka_host: %s**' % KAFKA_HOST)

KAFKA_PORT = str(os.getenv('KAFKA_PORT'))
print ('**kafka_port: %s**' % KAFKA_PORT)


def find(l, predicate):
    results = [x for x in l if predicate(x)]
    return results[0] if len(results) > 0 else None


def raise_for_status(r):
    http_error_msg = ''

    if 400 <= r.status_code < 500:
        http_error_msg = '%s Client Error: %s' % (r.status_code, r.reason)

    elif 500 <= r.status_code < 600:
        http_error_msg = '%s Server Error: %s' % (r.status_code, r.reason)

    return http_error_msg


def core_workflow_template(workflow_cr, wf_name, **kwargs):
    def _build_params(**dn):
        if dn is not None:
            return [dict(name=k, value=dn[k]) for k in dn]
        else:
            return None

    if wf_name:
        del workflow_cr['metadata']['generateName']
        workflow_cr['metadata']['name'] = wf_name

    workflow_cr['spec']['arguments']['parameters'] = _build_params(**kwargs)

    return workflow_cr

class Proxy:
    def __init__(self):
        """
        Initialize the proxy with the in-cluster configuration and the required
        APIs
        """
        kubernetes.config.load_incluster_config()
        self.api = kubernetes.client.CustomObjectsApi()
        self.core_api = kubernetes.client.CoreV1Api()
        sys.stdout.write('Proxy application initialized\n')

    def create_workflow(self, workflow_cr, wf_name=None, **kwargs):
        del workflow_cr['spec']['arguments']['parameters']
        workflow_cr = core_workflow_template(workflow_cr=workflow_cr,
                                             wf_name=wf_name,
                                             **kwargs)

        sys.stdout.write('[DEBUG] created skeleton: %s \n' % workflow_cr)

        sys.stdout.write('[INFO] about to submit workflow %s ...\n'
                         % workflow_cr)

        data = self.api.create_namespaced_custom_object(
            group='argoproj.io',
            version='v1alpha1',
            namespace=kwargs['namespace'],
            plural='workflows',
            body=workflow_cr)

        sys.stdout.write('Done creating workflow. data=[%s]\n' % data)
        return {
            'name': data['metadata']['name']
            }

    def get_workflow(self, namespace, name):
        sys.stdout.write('Requesting workflow for name '+name+'\n')

        workflow = self.api.get_namespaced_custom_object(
            group="argoproj.io",
            version="v1alpha1",
            namespace=namespace,
            plural="workflows",
            name=name)

        sys.stdout.write(str(workflow)+'\n')

        # list of dict name, value pairs
        workflow_parameters = workflow.get('spec', {}).get('arguments', {}).get('parameters', [])
        return {
            'name': workflow['metadata']['name'],
            'phase': workflow['status']['phase'],
            'progress': workflow['status']['progress'],
            'workflow_parameters': workflow_parameters
        }


proxy = flask.Flask(__name__)
proxy.debug = True
server = None

proxy_server = None


def setServer(s):
    global server
    server = s


def setProxy(p):
    global proxy_server
    proxy_server = p


def getMessagePayload():
    message = flask.request.get_json(force=True, silent=True)
    if message and not isinstance(message, dict):
        flask.abort(400, 'message payload is not a dictionary')
    else:
        value = message if (message or message == {}) else {}
    if not isinstance(value, dict):
        flask.abort(400, 'message payload did not provide binding for "value"')
    return value


@proxy.route("/hello")
def hello():
    sys.stdout.write ('Enter /hello\n')
    return ("Greetings from the Api server! ")


@proxy.route("/core",  methods=['POST'])
def core():
    """
    Create core.

    :param registry: url to private image registry to be used for the deployment. Optional
    :type registry: ``str``

    :param namespace: the namespace of the core to create
    :type namespace: ``str``

    :param cluster_core: the cluster of where the core is to be deployed
    :type cluster_core: ``str``

    :param networks: list of networks to create and used by the core network functions
            each entry includes the following attributes:
                "name": network name
                "master": the interface on the host to bound
                "range": range in cidr format
                "start": first ip in the range
                "end": last ip in the range
    :type networks: ``list`` of ``dict``
    """
    sys.stdout.write('Received core request\n')
    try:
        value = getMessagePayload()

        namespace = value.get('namespace')
        registry = value.get('registry', registry_private_free5gc)
        cluster= value['cluster']
        networks = value.get('networks')

        with open('/fiveg-core.yaml') as f:
            _yaml = yaml.load(f, Loader=yaml.FullLoader)

        res_json = proxy_server.create_workflow(
            workflow_cr=_yaml, namespace=namespace,
            registry=registry,
            cluster=cluster, networks=json.dumps(networks)
        )
        response = flask.jsonify(res_json)
        response.status_code = 200
        return response

    except HTTPException as e:
        sys.stdout.write('Exit /core %s\n' % str(e))
        return e

    except ApiException as e:
        response = flask.jsonify({'error': 'Reason: %s. Body: %s'
                                  % (e.reason, e.body)})
        response.status_code = e.status

    except Exception as e:
        response = flask.jsonify({'error': 'Internal error. {}'.format(e)})
        response.status_code = 500

    sys.stdout.write('Exit /core %s\n' % str(response))
    return response


@proxy.route("/subnetslice",  methods=['POST'])
def subnet():
    """
    Create a subnet slice.

    :param registry: url to private image registry to be used for the deployment. Optional
    :type registry: ``str``

    :param namespace: the namespace of the subnetslice to create
    :type namespace: ``str``

    :param cluster: the (edge) cluster of which the subnet will be deployed
    :type cluster: ``str``

    :param cluster_core: the cluster of where the core is deployed
    :type cluster_core: ``str``

    :param smf_name: the name of the SMF function instance to re-configure
    :type smf_name: ``str``

    :param core_namespace: the namespace of the core deployment
    :type core_namespace: ``str``

    :param sst: the sst of the slice e.g. "1"
    :type sst: ``str``

    :param sd: slice differentiator e.g. "010203"
    :type sd: ``str``

    :param pool: subnet (in cidr format) to be assigned to this UPF e.g. "60.61.0.0/16". Optional
                 Required for anchor UPF
    :type pool: ``str``

    :param connectedFrom: the id of a UPF, this subnetslice will be a child of,
                          in SMF ue topology
    :type connectedFrom: ``str``

    :param networks: list of networks to create and used by the slice functions
            each entry includes the following attributes:
                "name": network name
                "master": the interface on the host to bound
                "range": range in cidr format
                "start": first ip in the range
                "end": last ip in the range
    :type networks: ``list`` of ``dict``
    """
    sys.stdout.write('Received subnetslice request\n')
    try:
        value = getMessagePayload()

        namespace = value.get('namespace')
        registry = value.get('registry', registry_private_free5gc)

        kafka_ip = value.get('kafka_host', KAFKA_HOST)
        kafka_port = str(value.get('kafka_port', KAFKA_PORT))

        cluster_core = value['cluster_core']
        cluster = value['cluster']

        smf_name = value.get('smf_name', "smf-sample")
        core_namespace = value.get('core_namespace', "5g-core")
        sst = value.get('sst', "1")
        sd = value['sd']

        pool = value.get('pool', '0.0.0.0/16')
        connectedFrom = value['connectedFrom']

        network_name = value.get('network_name', 'OVERRIDE')
        network_master = value.get('network_master', 'OVERRIDE')
        network_range = value.get('network_range', 'OVERRIDE')
        network_start = value.get('network_start', 'OVERRIDE')
        network_end = value.get('network_end', 'OVERRIDE')
        networks = value.get('networks')

        with open('/fiveg-subnet.yaml') as f:
            _yaml = yaml.load(f, Loader=yaml.FullLoader)

        res_json = proxy_server.create_workflow(
            workflow_cr=_yaml, namespace=namespace,
            registry=registry,
            kafka_ip=kafka_ip, kafka_port=kafka_port,
            cluster_core=cluster_core, cluster=cluster,
            smf_name=smf_name, core_namespace=core_namespace, sst=sst, sd=sd,
            pool=pool, connectedFrom=connectedFrom,
            network_name=network_name,
            network_master=network_master,
            network_range=network_range,
            network_start=network_start,
            network_end=network_end, networks=json.dumps(networks)
        )
        response = flask.jsonify(res_json)
        response.status_code = 200
        return response

    except HTTPException as e:
        sys.stdout.write('Exit /subnetslice %s\n' % str(e))
        return e

    except ApiException as e:
        response = flask.jsonify({'error': 'Reason: %s. Body: %s'
                                  % (e.reason, e.body)})
        response.status_code = e.status

    except Exception as e:
        response = flask.jsonify({'error': 'Internal error. {}'.format(e)})
        response.status_code = 500

    sys.stdout.write('Exit /subnetslice %s\n' % str(response))
    return response


@proxy.route("/core_subnetslice/<namespace>/<name>",  methods=['GET'])
def get_core_subnetslice(namespace, name):
    """
    Get a subnet slice.

    :param namespace: the namespace of the subnetslice to retrieve
    :type namespace: ``str``

    :param name: the name of the subnetslice to create
    :type name: ``str``
    """
    try:
        flow_json = proxy_server.get_workflow(namespace, name)
        response = flask.jsonify(flow_json)
        response.status_code = 200
        return response
    except HTTPException as e:
        return e
    except Exception as e:
        response = flask.jsonify({'error': 'Internal error. {}'.format(e)})
        response.status_code = 500
        return response


@proxy.route("/subnetslice/<namespace>/<name>",  methods=['DELETE'])
def delete_subnet(namespace, name):
    """
    Delete a subnet slice.

    :param namespace: the namespace of the subnetslice to delete
    :type namespace: ``str``

    :param name: the name of the subnetslice to delete
    :type name: ``str``
    """
    sys.stdout.write('Received delete subnetslice request\n')
    try:
        with open('/fiveg-subnet-delete.yaml') as f:
            _yaml = yaml.load(f, Loader=yaml.FullLoader)

        proxy_server.create_workflow(
            workflow_cr=_yaml, wf_name='delete-%s' % name,
            namespace=namespace,
            fiveg_subnet_id=name
        )

        response = flask.jsonify({'OK': 204})
        response.status_code = 204

    except HTTPException as e:
        sys.stdout.write('Exit delete /subnetslice %s\n' % str(e))
        return e

    except ApiException as e:
        response = flask.jsonify({'error': 'Reason: %s. Body: %s'
                                  % (e.reason, e.body)})
        response.status_code = e.status

    except Exception as e:
        response = flask.jsonify({'error': 'Internal error. {}'.format(e)})
        response.status_code = 500

    sys.stdout.write('Exit delete /subnetslice %s\n' % str(response))
    return response
    


def main():
    port = int(os.getenv('LISTEN_PORT', 8080))
    server = WSGIServer(('0.0.0.0', port), proxy, log=None)
    setServer(server)
    server.serve_forever()


if __name__ == '__main__':
    setProxy(Proxy())
    main()
