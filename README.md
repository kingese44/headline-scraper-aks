# Headline Scraper on AKS

A small Python app that scrapes headlines from a list of news sites and shows them on a web page. It runs on Azure Kubernetes Service (AKS), which is created with Terraform and exposed through a load balancer and Traefik.

I built with Python, Docker, Terraform and Kubernetes together. 

## Architecture

```
Browser -> Azure Load Balancer (public IP) -> Traefik -> Service "headlines" -> Pod (Flask app)
```

- **Flask app**: downloads each site with `requests` and extracts `h1`/`h2`/`h3` tags with BeautifulSoup.
- **Docker**: packages the app as an image, pushed to Docker Hub.
- **Terraform**: creates the AKS cluster.
- **Kubernetes**: a Deployment runs the app and a Service gives it a stable address.
- **Traefik**: the ingress controller. Its Service has type `LoadBalancer`, so AKS asks Azure for the public IP.
- **Ingress**: routes `/` to the `headlines` Service.

## Repository layout

```
app/         Python app, Dockerfile, requirements.txt
terraform/   AKS cluster (main.tf, variables.tf, outputs.tf)
k8s/         deployment.yaml, service.yaml, ingress.yaml
```

## Steps

### 1. Run locally

```bash
cd app
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python app.py
```

Open http://localhost:8080.

### 2. Build and push the image

```bash
docker build -t headlines:1 app
docker tag headlines:1 YOUR_DOCKERHUB_USER/headlines:1
docker push YOUR_DOCKERHUB_USER/headlines:1
```

Then set your username in `k8s/deployment.yaml`. The Docker Hub repo must be public so AKS can pull it without credentials.

### 3. Create the cluster

From Azure Cloud Shell (or any shell where `az login` has been run):

```bash
cd terraform
export ARM_SUBSCRIPTION_ID=$(az account show --query id --output tsv)
export TF_VAR_resource_group_name="YOUR_RESOURCE_GROUP"
terraform init
terraform plan
terraform apply
az aks get-credentials --resource-group YOUR_RESOURCE_GROUP --name headlines-aks
kubectl get nodes
```

The subscription ID and resource group are passed as environment variables, so nothing sensitive is stored in the code.

### 4. Deploy the app

```bash
kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
kubectl get pods
```

### 5. Install Traefik

```bash
helm repo add traefik https://traefik.github.io/charts
helm repo update
helm install traefik traefik/traefik --namespace traefik --create-namespace
kubectl get svc -n traefik
```

Wait until `EXTERNAL-IP` shows an address.

### 6. Route traffic to the app

```bash
kubectl apply -f k8s/ingress.yaml
```

Open `http://EXTERNAL-IP` in a browser to see the headlines.

## Problems I hit and how I fixed them

| Problem | Cause | Fix |
|---|---|---|
| `RequestDisallowedByPolicy` (403) when creating the cluster | The lab's Azure Policy only allows a node pool named `agentpool`, one node, and certain VM sizes | Read the policy with `az policy definition show` and renamed the node pool to `agentpool` |
| `docker build` could not find the Dockerfile | The files existed but were empty or missing | Checked file sizes with `dir`, recreated the files |
| `cannot connect to the Docker daemon` | Docker Desktop was not running | Started Docker Desktop and waited for "Engine running" |
| Docker image name rejected | Docker Hub names must be lowercase | Used the lowercase username |
| `git push` failed with `SEC_E_ALGORITHM_MISMATCH` | Windows schannel TLS settings | `git config --global http.sslBackend openssl` |
| Undeclared variable in Terraform | `variables.tf` was empty after pasting | Recreated the file and checked it with `cat` |

## Working with a lab that resets every 4 hours

Everything in Azure disappears on reset, so the repo holds all the code needed to rebuild it. Cloud Shell files are lost too, so the code lives here, and the Docker image lives on Docker Hub so it survives resets. After a reset: start with a clean Terraform state, then run steps 3 to 6 again.

## Cleanup

In a real subscription, remove the cluster to stop charges:

```bash
cd terraform
terraform destroy
```

## Known limitations and next steps

- The scraper takes every heading tag, so it picks up section titles like "News" and "More to explore", and some site labels run into the headline text.
- Each page load scrapes the sites live. Caching the results for a few minutes would be faster and kinder to the news sites.
- Flask's development server is used. A production setup would use gunicorn.
- Add HTTPS with a certificate, and store Terraform state remotely.