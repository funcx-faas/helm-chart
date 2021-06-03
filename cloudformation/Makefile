
cluster: 
	eksctl create cluster -f clusterconfig.yml


install-alb-controler:
	helm repo add eks https://aws.github.io/eks-charts
	helm upgrade -i aws-load-balancer-controller eks/aws-load-balancer-controller -n kube-system --set clusterName=funcx-prod --set serviceAccount.create=false --set serviceAccount.name=aws-load-balancer-controller --set region=us-east-1 --set vpcId=vpc-0d3b9f7c3a9c6c1ba
