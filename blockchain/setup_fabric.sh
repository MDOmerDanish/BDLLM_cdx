#!/bin/bash

echo "Executing hard reset of Fabric environment..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/fabric-samples/test-network/" || exit
echo "Tearing down existing network structures..."
./network.sh down
echo "Purging orphaned Docker containers, networks, and ghost volumes..."
docker container prune -f
docker network prune -f
docker volume prune -f
echo "Wiping leftover cryptographic artifacts..."
rm -rf organizations/peerOrganizations organizations/ordererOrganizations channel-artifacts
echo "Rebuilding Fabric network and channel..."
./network.sh up createChannel -c bdllmchannel
