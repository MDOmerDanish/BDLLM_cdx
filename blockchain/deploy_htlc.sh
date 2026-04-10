#!/bin/bash
echo "Enforcing strict directory isolation..."

# 1. Purge any lingering module files from the root directory
rm -f go.mod go.sum

# 2. Navigate explicitly into the chaincode folder
cd blockchain/chaincode || exit

echo "Initializing Go dependencies for HTLC chaincode..."
rm -f go.mod go.sum
go mod init htlc
go mod tidy

# 3. Navigate to the Fabric test network
cd ../../fabric-samples/test-network/ || exit

echo "Deploying HTLC to Fabric channel..."
./network.sh deployCC -ccn htlc -ccp ../../blockchain/chaincode/ -ccl go -c bdllmchannel

echo "Deployment script execution finished."
