# On-Chain Architecture

## Fabric Test Network Breakdown
```
+----------------------------------------------------+
| Hyperledger Fabric Test Network                     |
|  +--------------------+   +--------------------+   |
|  | Peer0.Org1         |   | Orderer            |   |
|  | (chaincode lifecycle|   | (consensus,        |   |
|  | endorsement)        |   | channel creation)  |   |
|  +--------------------+   +--------------------+   |
|             |                     |                  |
|             v                     v                  |
|  +--------------------------------------------+     |
|  | setup_fabric.sh                            |     |
|  | - ./network.sh down                         |     |
|  | - prune containers/networks/volumes        |     |
|  | - wipe crypto artifacts + channel-artifacts|     |
|  | - ./network.sh up createChannel -c bdllmchannel |  |
|  +--------------------------------------------+     |
+----------------------------------------------------+
```

`setup_fabric.sh` performs a hard reset: it tears down all existing Fabric containers, prunes Docker artifacts, removes `organizations/` and `channel-artifacts/`, and then brings the `test-network` back up with the `bdllmchannel` channel so that subsequent deployments start from a deterministic baseline.

## Deployment Lifecycle
```
+----------------------------------------------------+
| HTLC Chaincode Deployment                          |
|  +--------------------------------------------+     |
|  | deploy_htlc.sh                              |     |
|  | 1. cd blockchain/chaincode/                 |     |
|  | 2. rm go.mod go.sum; go mod init htlc; go mod tidy | |
|  | 3. cd ../fabric-samples/test-network/       |     |
|  | 4. ./network.sh deployCC -ccn htlc ...      |     |
|  +--------------------------------------------+     |
+----------------------------------------------------+
```

The deployment script reinitializes the HTLC Go module inside `blockchain/chaincode/`, ensuring a clean `go.mod`/`go.sum`, and then calls Fabric's `network.sh deployCC` to install, approve, and commit the `htlc` chaincode onto `bdllmchannel`, pointing the `ccp` flag back to the local chains.

## Chaincode Structure
```
+---------------------------------------------------------+
| HTLC Chaincode (chaincode/htlc.go)                      |
|  +--------------------------+                           |
|  | HTLCContract struct      |                           |
|  | - MintTokens(...)        |                           |
|  | + modifyBalance() helper |                           |
|  +--------------------------+                           |
|                   |                                      |
|                   v                                      |
|  +-------------------------------+   +-----------------+  |
|  | CreateLock(...)               |   | Claim(...)      |  |
|  | - ensure unique contractID    |   | - verify preimage|  |
|  | - deduct sender balance       |   | - credit receiver|  |
|  | - snapshot expiration via tx  |   | - mark CLAIMED   |  |
|  +-------------------------------+   +-----------------+  |
|                      |                                      |
|                      v                                      |
|                 +--------+                                   |
|                 | Refund |                                   |
|                 | - ensure timelock expired                 |
|                 | - return funds to sender                  |
|                 | - mark REFUNDED                           |
|                 +--------+                                   |
+---------------------------------------------------------+
```

`chaincode/htlc.go` keeps balances under `balance_<userID>` keys via the unexported `modifyBalance` helper. `CreateLock` ensures the sender has enough balance, escrowed amount, and records `hashLock`/`timeLock` with status `LOCKED`. `Claim` recomputes SHA-256 preimage hashes, routes funds to the receiver, and updates status to `CLAIMED`. `Refund` checks the current Fabric timestamp versus `TimeLock`, returns funds to the sender, and flips the status to `REFUNDED` so the contract cannot be replayed.
