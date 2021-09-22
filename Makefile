DEV_CONF=deployed_values/dev.yaml
WEB_SERVICE_LOCAL_PORT=5000
WEBSOCKET_SERVICE_LOCAL_PORT=6000

.PHONY: dev-up dev-down
dev-down:
	$(MAKE) stop-port-forward
	$(MAKE) shutdown-local-cluster
dev-up:
	$(MAKE) start-local-cluster
	$(MAKE) start-port-forward

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
	-pkill -f 'kubectl port-forward funcx-funcx-websocket-service'
	-pkill -f 'kubectl port-forward funcx-funcx-web-service'
	@echo "\n= port forwarding stopped\n"

.PHONY: start-local-cluster shutodwn-local-cluster
start-local-cluster:
	@echo "\n= start local cluster"
	@echo "== helm install (CONF=$(DEV_CONF), timeout=3 minutes)\n"
	helm install --atomic --timeout 3m0s -f "$(DEV_CONF)" funcx funcx
	@echo "\n= local cluster started\n"
shutdown-local-cluster:
	@echo "\n= shutdown local cluster\n"
	helm uninstall funcx
	@echo "\n= local cluster shutdown complete\n"
