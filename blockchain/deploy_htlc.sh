#!/bin/bash
echo "Enforcing strict directory isolation..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Navigate explicitly into the chaincode folder
cd "$SCRIPT_DIR/chaincode" || exit

echo "Initializing Go dependencies for HTLC chaincode..."
rm -f go.mod go.sum
go mod init htlc
go mod tidy

# 2. Navigate to the local Fabric test network
cd "$SCRIPT_DIR/fabric-samples/test-network/" || exit

echo "Deploying HTLC to Fabric channel..."
# Ensure the chaincode path targets the blockchain directory correctly
./network.sh deployCC -ccn htlc -ccp ../../chaincode/ -ccl go -c bdllmchannel

echo "Deployment script execution finished."
