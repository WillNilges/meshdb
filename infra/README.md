# Meshdb Environment Setup

These instructions will set up a 4 node k3s cluster on proxmox.
- 1 "manager" node for control plane and to be used for deployments.
- 3 "agent" nodes to run services.

1. Configure a user for the [proxmox provider](https://registry.terraform.io/providers/Telmate/proxmox/latest/docs) and set up env vars. Create an API key in Proxmox, and disable Privilege Separation.
2. Setup tfvars + ssh keys
```
cd meshdb/infra/tf/
cp example.tfvars your_env.tfvars
# Modify your_env.tfvars to meet your needs
ENV_NAME="garfield" # Matching meshdb_env_name
ssh-keygen -t ed25519 -f ./meshdb$ENV_NAME
```
3. Create the VMs that will host k3s
```
terraform init
terraform plan --var-file=your_env.tfvars
terraform apply --var-file=your_env.tfvars
```
4. Login via serial and figure out the IPs that were received from DHCP
5. One time provisioning for the manager node

```
target_host="<MGR IP>"
scp infra/mgr_provision.sh ubuntu@$target_host:/home/ubuntu/mgr_provision.sh
ssh -t ubuntu@$target_host "sudo bash /home/ubuntu/mgr_provision.sh"
```

6. Set the IP range for metallb, such as `10.70.90.80/29`, in `/opt/meshdb_mgmt/meshdb/infra/cluster/metallb_extra.yaml` and then deploy metallb and longhorn from the manager
```
cd /opt/meshdb_mgmt/meshdb/infra/cluster/
terraform init
terraform plan
terraform apply
# update address block in /opt/meshdb_mgmt/meshdb/infra/cluster/metallb_extra.yaml
kubectl apply -f /opt/meshdb_mgmt/meshdb/infra/cluster/metallb_extra.yaml
```

7. Setup each node (from the manager)

```
cd /opt/meshdb_mgmt/meshdb/infra/
declare -a target_nodes=("10.70.90.XX" "10.70.90.YY" "10.70.90.ZZ")

for n in "${target_nodes[@]}"
do
  bash setup_node.sh $n
done
```

8. Update values + secrets in `/opt/meshdb_mgmt/values.yaml` and `/opt/meshdb_mgmt/secret.values.yaml`

9. Deploy helm chart. Create the namespace you indicated in `/opt/meshdb_mgmt/values.yaml`

```
your_ns="meshdbdev0"
cd /opt/meshdb_mgmt/meshdb/infra/helm/meshdb/
kubectl create namespace $your_ns
helm template . -f ../../../../values.yaml -f ../../../../secret.values.yaml | kubectl apply -f -
kubectl get all -n $your_ns
```

10. If you need a superuser: `kubectl exec -it -n meshdbdev0 service/meshdb-meshweb bash` and `python manage.py createsuperuser`