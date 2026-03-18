#!/bin/bash

# Download the official Hyperledger Fabric install script
curl -o install-fabric.sh https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/install-fabric.sh

# Make the script executable
chmod +x install-fabric.sh

# Run the script to fetch Docker images, binaries, and fabric-samples repository
./install-fabric.sh docker binary samples

# Navigate to the test-network directory
cd fabric-samples/test-network

# Bring up the network, create a channel named 'bdllmchannel', and use Certificate Authorities
./network.sh up createChannel -c bdllmchannel -ca