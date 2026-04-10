# Hyperledger Fabric Architecture

## Chaincode Architecture
```
+-------------------------------------+
| Chaincodes                          |
|  +--------------------------------+ |
|  | htlc (Go)                      | |
|  | + LockFunds(contractID,...)    | |
|  | + ClaimFunds(contractID,...)   | |
|  | + Refund(contractID)           | |
|  +--------------------------------+ |
+-------------------------------------+
```
The `htlc` Go chaincode owns deterministic escrow state: it stores contract IDs, sender/receiver balances, hash locks, timelocks, and transition statuses. LockFunds deducts the sender balance before persisting the contract; ClaimFunds verifies the hashed preimage before routing funds to the receiver and updating status to `CLAIMED`; Refund ensures the timelock has expired before returning the balance to the sender and marking `REFUNDED`.

## Deployment Lifecycle
1. `blockchain/setup_fabric.sh` enforces a hard reset of the Fabric test network: it tears down stray containers, prunes volumes if needed, and brings up the peers/orderer/CA stack so that ledger state starts clean. This script protects against leftover artifacts by trimming Docker volumes and reinitializing the `test-network` directory.
2. `blockchain/deploy_htlc.sh` handles the Go chaincode packaging: it enters `chaincode/`, (re)initializes the Go module to guarantee the correct `go.mod`, fetches tidy dependencies, and then executes Fabric's `network.sh deployCC` command to install and approve `htlc` on `bdllmchannel`. The script seals the flow by returning the CLI to the workspace root when deployment completes.
