ENVIRONMENT?=dev

.PHONY: cluster
create-cluster: 
	eksctl create cluster -f clusterconfig-$(ENVIRONMENT).yml

update-cluster:
	eksctl update cluster -f clusterconfig-$(ENVIRONMENT).yml --approve
	eksctl update iamserviceaccount -f clusterconfig-$(ENVIRONMENT).yml --approve

.PHONY: install-alb-controler
install-alb-controler:
	helm repo add eks https://aws.github.io/eks-charts
	helm repo update eks
	helm upgrade -i aws-load-balancer-controller --version 1.2.7 eks/aws-load-balancer-controller -n kube-system --set clusterName=funcx-$(ENVIRONMENT) --set serviceAccount.create=false --set serviceAccount.name=aws-load-balancer-controller --set region=us-east-1 --set vpcId=vpc-0d3b9f7c3a9c6c1ba
	kubectl apply -f external-dns.yaml --namespace kube-system

.PHONY: install-fluentbit
install-fluentbit:
	kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/cloudwatch-namespace.yaml
	
	kubectl create configmap fluent-bit-cluster-info \
	--from-literal=cluster.name=funcx-$(ENVIRONMENT) \
	--from-literal=http.server=Off \
	--from-literal=http.port=2020 \
	--from-literal=read.head=Off \
	--from-literal=read.tail=On \
	--from-literal=logs.region=us-east-1 -n amazon-cloudwatch
	
	kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/fluent-bit/fluent-bit.yaml
