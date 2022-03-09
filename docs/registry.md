# Private registry

Allocate a dedicated VM Ubuntu 20.04 with: 2 vCPU, 8 GB RAM, 100 GB disk (or more depending on the images to store)

**Important:** ensure this VM is accessible from worker nodes on both core and edge clusters

## Start private docker registry

Log into the VM where the registry is going to run

```
sudo docker run -d -p 5000:5000 --name registry registry:2
```

Note: It's **important** to use port `5000`

## Update docker client nodes

Do this for all master and worker nodes on both core and edge clusters

```
vi /etc/docker/daemon.json
```

add the registry with VM's public ipaddress per the below example

```
{
  "insecure-registries":["172.15.0.167:5000"]
}
```

restart docker

```
service docker stop
service docker start
```

## Copy images into registry

Update `ansible/inventory.yaml` accordingly

**Tip:** you may need to update [main.yaml](../ansible/roles/xnfs/tasks/main.yaml) with proper `origin` and `target`

```
cd ~/issm-mec-cnmp/ansible
ansible-playbook -i inventory.yaml entrypoint.yaml
```
