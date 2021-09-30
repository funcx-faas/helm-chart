DEV_CONF=deployed_values/values.yaml
WEB_SERVICE_LOCAL_PORT=5000
WEBSOCKET_SERVICE_LOCAL_PORT=6000
HELM_TIMEOUT=3m0s

.PHONY: dev-up dev-down dev-update
dev-down:
	$(MAKE) stop-port-forward
	$(MAKE) shutdown-local-cluster
dev-up:
	$(MAKE) start-local-cluster
	$(MAKE) start-port-forward
dev-update:
	helm upgrade --atomic --timeout $(HELM_TIMEOUT) -f "$(DEV_CONF)" funcx funcx

.PHONY: start-port-forward stop-port-forward
start-port-forward:
	@echo "\n= start port forwarding\n"
	WEB_SERVICE_LOCAL_PORT=$(WEB_SERVICE_LOCAL_PORT) \
		WEBSOCKET_SERVICE_LOCAL_PORT=$(WEBSOCKET_SERVICE_LOCAL_PORT) \
		./local_dev/daemonized-port-forward
	@echo "\n= port forwarding started\n"
# use 'pkill -f' to look at full command lines
# be specific: match on these specific port forwarding commands to avoid
# interfering with any other forwarding that the caller may have setup
stop-port-forward:
	@echo "\n= stop port forwarding\n"
	-pkill -f 'kubectl port-forward service/funcx-funcx-websocket-service'
	-pkill -f 'kubectl port-forward service/funcx-funcx-web-service'
	@echo "\n= port forwarding stopped\n"

.PHONY: start-local-cluster shutodwn-local-cluster
start-local-cluster:
	@echo "\n= start local cluster"
	@echo "== helm install\n"
	helm install --atomic --timeout $(HELM_TIMEOUT) -f "$(DEV_CONF)" funcx funcx
	@echo "\n= local cluster started\n"
shutdown-local-cluster:
	@echo "\n= shutdown local cluster\n"
	helm uninstall funcx
	@echo "\n= local cluster shutdown complete\n"

.PHONY: lint
lint:
	pre-commit run -a
.PHONY: test-local
test-local:
	pytest smoke_tests/ --funcx-config local
