# Adding a GitHub Actions User to Cluster
We created a captive IAM user to be operated by GitHub actions for CI jobs. It
has very limited powers. Here are the steps to grant it access to the dev
cluster.

### Grant the IAM user DescribeCluster Permissions on the Cluster
We will need this to get the Kube config file
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "eks:DescribeCluster",
            "Resource": "arn:aws:eks:us-east-1:_______________:cluster/funcx-dev"
        }
    ]
}
```

### Create the role and rolebindings for the github_actions group
``` bash
kubectl create -f eks-github-action-access.yaml
```
This creates `eks-github-action-role` which is only allowed to list, delete, and 
patch deployments. It also creates a rolebinding for a group called 
`github-action-binding`

### Add new user to EKS
Edit the aws-auth configMap with
```bash
kubectl edit -n kube-system configmap/aws-auth
```

You will need to edit the `mapUsers` property. It should look like:
```yaml
  mapUsers: |
    - userarn: <githubactions ARN>
      username: githubactions
      groups:
        - github-action-binding
```

### Map the user to the role
Finally load in the role binding between the user and the role:
```
kubectl create -f githubactions-role-binding.yaml
```

### Put the KubeConfig as a GitHub Repo Secret
The github action requires the AWS ID and Secret in order to connect to EKS.
It also needs a base64 encoded version of the kube config file downloaded from 
EKS. 

Download the kube config file by adding a profile for this user to 
`.aws/credentials` and using this command:
```bash
aws eks update-kubeconfig --profile funcx_github_actions --name funcx-dev    
```

I found that my file had an env setting for `AWS_PROFILE` which tied the 
kubeconfig to the profile in my local `.aws/credentials` file. This didn't 
work from the action, so I deleted the `env` section from my kube config.

Create the Profile by:
```yaml
 cat ~/.kube/funcx-dev-github-staging| base64
```

and paste the results in as the `KUBE_CONFIG_DATA_STAGING` Secret.

## Install Sealed Secrets
We use Bitnami's Sealed Secrets Controller to allow us to check all of the
config into GitHub. 

Install sealed secrets helm chart
```bash
 helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets       
 helm install sealed-secrets --namespace kube-system sealed-secrets/sealed-secrets
```

You will need the `kubeseal` command on your computer. Follow instructions for
[the various options](https://github.com/bitnami-labs/sealed-secrets#homebrew)



