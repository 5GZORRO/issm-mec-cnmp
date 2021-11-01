import flask
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
import re


registry_private_free5gc = os.getenv('REGISTRY_PRIVATE_FREE5GC')
print ('**registry_private_free5gc: %s**' % registry_private_free5gc)

namespace = os.getenv('NAMESPACE')
print ('**namespace: %s**' % namespace)


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


def core_workflow_template(workflow_cr, **kwargs):
    def _build_params(**dn):
        if dn is not None:
            # if network_name provided, it is assumed that *all* network attrs there
            # as well
            return [dict(name=k, value=dn[k]) for k in dn]
#             if 'network_name' not in kwargs:
#                 l = l + ([dict(name='network_name', value='OVERRIDE'),
#                           dict(name='network_master', value='OVERRIDE'),
#                           dict(name='network_range', value='OVERRIDE'),
#                           dict(name='network_start', value='OVERRIDE'),
#                           dict(name='network_end', value='OVERRIDE')])
#             return l
        else:
            return None

    workflow_cr['metadata']['name'] = 'fiveg-subnet-%s' % kwargs['sd']
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

    def create_workflow(self, workflow_cr, **kwargs):
        del workflow_cr['spec']['arguments']['parameters']
        workflow_cr = core_workflow_template(workflow_cr=workflow_cr, **kwargs)

        sys.stdout.write('[DEBUG] created skeleton: %s \n' % workflow_cr)

        sys.stdout.write('[INFO] about to submit workflow %s ...\n'
                         % workflow_cr)

        global namespace
        self.api.create_namespaced_custom_object(
            group='argoproj.io',
            version='v1alpha1',
            namespace=namespace,
            plural='workflows',
            body=workflow_cr)

        sys.stdout.write('Done creating workflow\n')
        return {
            'workflow_name': workflow_cr['metadata']['name']
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


@proxy.route("/subnetslice",  methods=['POST'])
def subnet():
    """
    Create a subnet slice.

    :param registry: url to private image registry to be used for the deployment. Optional
    :type registry: ``str``

    :param cluster_core: the cluster of where the core is deployed
    :type cluster_core: ``str``

    :param cluster_edge: the edge (cluster) of which the subnet will be deployed
    :type cluster_edge: ``str``

    :param smf_name: the name of the SMF function instance to re-configure
    :type smf_name: ``str``

    :param sst: the sst of the slice e.g. "1"
    :type sst: ``str``

    :param sd: slice differentiator e.g. "010203"
    :type sd: ``str``

    TODO: add network parameters..
    """
    sys.stdout.write('Received subnetslice request\n')
    try:
        value = getMessagePayload()

        registry = value.get('registry', registry_private_free5gc)
        cluster_core = value['cluster_core']
        cluster_edge = value['cluster_edge']

        smf_name = value.get('smf_name', "smf-sample")
        sst = value.get('sst', "1")
        sd = value['sd']

        network_name = value.get('network_name', 'OVERRIDE')
        network_master = value.get('network_master', 'OVERRIDE')
        network_range = value.get('network_range', 'OVERRIDE')
        network_start = value.get('network_start', 'OVERRIDE')
        network_end = value.get('network_end', 'OVERRIDE')

        with open('/fiveg-subnet.yaml') as f:
            fiveg_subnet_yaml = yaml.load(f, Loader=yaml.FullLoader)

        res_json = proxy_server.create_workflow(
            workflow_cr=fiveg_subnet_yaml, registry=registry,
            cluster_core=cluster_core, cluster_edge=cluster_edge,
            smf_name=smf_name, sst=sst, sd=sd,
            network_name=network_name,
            network_master=network_master,
            network_range=network_range,
            network_start=network_start,
            network_end=network_end
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


def main():
    port = int(os.getenv('LISTEN_PORT', 8080))
    server = WSGIServer(('0.0.0.0', port), proxy, log=None)
    setServer(server)
    server.serve_forever()


if __name__ == '__main__':
    setProxy(Proxy())
    main()
