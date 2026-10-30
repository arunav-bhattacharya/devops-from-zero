# Dynatrace (Days 50 and 51)

Files in this folder:

| File | Used on | What it is |
|---|---|---|
| `queries.dql` | Days 50 and 51 | Every DQL query from the lessons. Paste one query at a time into a Notebook. |
| `dynakube.yaml` | Day 51 (optional) | The DynaKube for the course's kind cluster: app-only monitoring and one small ActiveGate. |
| `README.md` | Day 51 (optional) | This file: install, check and uninstall steps. |

## Cost first

- The **Playground** is free and needs no install. It has sample data. Do Day 50 and the DQL part of Day 51 there.
- The **free trial** of Dynatrace SaaS lasts 15 days, and the sign-up page says no credit card is needed. The 15 days start when you sign up, so start it only when you have time to do the kind install below.
- After the trial, Dynatrace is paid (the Dynatrace Platform Subscription). Ingesting data, keeping it and querying it are all metered.
- Check the current terms on the [try-free page](https://www.dynatrace.com/try-free) before you sign up.

## Before you start (optional part)

**Kind and Apple Silicon Macs are not officially supported by Dynatrace.** The images exist for arm64 and Dynatrace tests its Operator on kind in CI, but on your laptop this may fail. If it does, use the trial with Dynatrace's GitHub Codespaces lab instead: <https://github.com/Dynatrace/obslab-release-validation>.

You need:

- the kind cluster from Day 30 (`kind create cluster --name devops --config kind-config.yaml`) with hello-devops running in the `hello` namespace (`kubectl apply -k k8s`)
- Helm 4 and kubectl (Day 2)
- a Dynatrace trial environment. Its address looks like `https://abc12345.apps.dynatrace.com`; `abc12345` is your environment ID.

Install commands and versions change. Check the current Dynatrace Operator docs and the
[Operator releases](https://github.com/Dynatrace/dynatrace-operator/releases) before you copy them. This file was written for Operator v1.11.1.

## 1. Get a token

The easiest way is to let Dynatrace make the token. In your trial, open the QuickStart app (or the Kubernetes app) and pick the Kubernetes option. The page creates a token with the right permissions and puts it in the install command it shows. Copy only the token; you will use this folder's `dynakube.yaml` instead of the page's YAML.

A new environment gives you a **platform token** (it starts with `dt0s16.`). Older environments may give an **access token** (it starts with `dt0c01.`). The Operator accepts either one in the secret's `apiToken` key.

If you make the token yourself, these are the permissions (scopes) Dynatrace's own setup notes list for the Operator:

- access token: `InstallerDownload`, `settings.read`, `settings.write`, `activeGateTokenManagement.create` (the "Kubernetes: Dynatrace Operator" template sets them)
- platform token: `fleet-management:oneagents:download`, `fleet-management:oneagent.connection-info:read`, `fleet-management:oneagent.tokens:read`, `fleet-management:cluster-id:read`, `fleet-management:activegates:download`, `fleet-management:activegate.tokens:create`

The second token, `dataIngestToken`, is used for sending metrics. If you only have one token, use it twice, as Dynatrace's setup notes do.

Put the values into your shell without saving them in your history:

```bash
cd ~/code/hello-devops
export DT_ENV_ID=abc12345            # your environment ID (not secret)
echo "Paste the API token, then press Enter:"
read -rs DT_API_TOKEN && export DT_API_TOKEN
echo "Paste the data ingest token (or the same token again), then press Enter:"
read -rs DT_DATA_INGEST_TOKEN && export DT_DATA_INGEST_TOKEN
```

Never commit a token. If one leaks, delete it in Dynatrace and make a new one.

## 2. Install the Dynatrace Operator

With Helm (the chart is in an OCI registry). `csidriver.enabled=false` skips the CSI driver, which app-only monitoring does not need, so there are fewer moving parts on kind. `--rollback-on-failure` is the Helm 4 name for the old `--atomic`.

```bash
helm upgrade --install dynatrace-operator oci://public.ecr.aws/dynatrace/dynatrace-operator \
  --version 1.11.1 \
  --namespace dynatrace --create-namespace \
  --set csidriver.enabled=false \
  --rollback-on-failure
```

Without Helm, apply the release manifest (the variant without the CSI driver):

```bash
kubectl create namespace dynatrace
kubectl apply -f https://github.com/Dynatrace/dynatrace-operator/releases/download/v1.11.1/kubernetes.yaml
kubectl -n dynatrace wait pod --for=condition=ready \
  --selector=app.kubernetes.io/name=dynatrace-operator,app.kubernetes.io/component=webhook \
  --timeout=300s
```

## 3. Create the secret

The secret must be called `dynakube`, like the DynaKube. `printf` is built into the shell and `<(...)` hands kubectl a temporary file, so the token never appears in the process list.

```bash
kubectl -n dynatrace create secret generic dynakube \
  --from-env-file=<(printf 'apiToken=%s\ndataIngestToken=%s\n' "$DT_API_TOKEN" "$DT_DATA_INGEST_TOKEN") \
  --dry-run=client -o yaml | kubectl apply -f -
```

## 4. Choose what to monitor, then apply the DynaKube

```bash
# Only labelled namespaces get OneAgent. (If Argo CD manages "hello", add the label in git instead.)
kubectl label namespace hello monitoring=dynatrace

# Let the Operator's webhook check the file first. It explains most mistakes.
sed "s/ENVIRONMENTID/$DT_ENV_ID/" dynatrace/dynakube.yaml | kubectl apply --dry-run=server -f -

# Apply it for real.
sed "s/ENVIRONMENTID/$DT_ENV_ID/" dynatrace/dynakube.yaml | kubectl apply -f -

# OneAgent is added when a pod starts, so restart the app's pods.
kubectl -n hello rollout restart deployment/hello-devops
kubectl -n hello rollout status deployment/hello-devops
```

## 5. Check it worked

```bash
kubectl -n dynatrace get dynakube          # STATUS should become Running (Deploying first)
kubectl -n dynatrace get pods              # operator, webhook and dynakube-activegate-0
kubectl -n hello get pods -o jsonpath='{.items[0].spec.initContainers[*].name}'; echo
# prints dynatrace-operator: the webhook added its init container to the pod
```

Send some traffic (`curl localhost:8081` a few times, the kind NodePort from Day 33), wait a few minutes, then look in Dynatrace:

- the Kubernetes app: a cluster called `kind-devops` with its nodes, namespaces and workloads
- the Services app: a hello-devops service, if OneAgent could instrument the Python app (recent OneAgent versions support Python and Flask; check the technology support page if it does not show up)
- a Notebook: run the Day 51 queries from `queries.dql`

If something fails:

| What you see | Likely cause | What to try |
|---|---|---|
| DynaKube stays `Deploying` or shows `Error` | wrong environment ID or token permissions | `kubectl -n dynatrace describe dynakube dynakube` and `kubectl -n dynatrace logs deploy/dynatrace-operator` |
| `dynakube-activegate-0` is `Pending` | not enough memory in Docker Desktop | `kubectl -n dynatrace describe pod dynakube-activegate-0`; give Docker more memory or lower the request |
| `ImagePullBackOff` | image or architecture problem on arm64 | `kubectl -n dynatrace describe pod <name>`; this is the "may fail" case |
| no init container in the hello pods | namespace not labelled, or pods not restarted | check `kubectl get namespace hello --show-labels`, then restart the deployment |

## 6. Uninstall (in this order)

Delete the DynaKube first and let the Operator clean up. If you delete the namespace or the CRDs first, the namespace can stay stuck in `Terminating`.

```bash
kubectl -n dynatrace delete dynakube --all
kubectl -n dynatrace wait --for=delete dynakube --all --timeout=60s
helm uninstall dynatrace-operator -n dynatrace      # or: kubectl delete -f <the manifest URL>
kubectl get crd -o name | grep 'dynatrace\.com$' | xargs -r kubectl delete
kubectl delete namespace dynatrace
kubectl label namespace hello monitoring-
kubectl -n hello rollout restart deployment/hello-devops   # start pods without OneAgent
```

Then delete the token in Dynatrace.

## Sources

- Dynatrace Operator (code, samples, releases): <https://github.com/Dynatrace/dynatrace-operator>
- The official app-only sample this file is based on: <https://github.com/Dynatrace/dynatrace-operator/blob/v1.11.1/assets/samples/dynakube/v1beta6/applicationMonitoring.yaml>
- Dynatrace's own setup notes for AI tools (token types, secret, uninstall order): <https://github.com/Dynatrace/dynatrace-for-ai>
- Kubernetes deployment options: <https://docs.dynatrace.com/docs/ingest-from/setup-on-k8s/deployment>
