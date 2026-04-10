# BDLLM Documentation Hub

BDLLM (Blockchain Distributed LLM Marketplace) unifies a Python-powered orchestration layer with a Hyperledger Fabric-backed ledger so that inference providers, clients, and contract logic can be audited end-to-end.

## System Architecture: On-Chain vs. Off-Chain
```
+---------------------------------------------+
| Off-Chain Components                        |
|  +---------------------+    +-------------+ |
|  | Python Orchestrator |--->| LLM Server  | |
|  | (manager.py)        |    | overlay     | |
|  +---------------------+    +-------------+ |
|             |                     ^         |
|             v                     |         |
|         +-----------+------------+         |
|         | LLM Client|<---------------------+
|         +-----------+                      |
+---------------------------------------------+
| On-Chain Components                         |
|  +------------------------------+           |
|  | Hyperledger Fabric Test      |           |
|  | Network (peers, orderer, CA) |           |
|  +------------------------------+           |
|              |                              |
|              v                              |
|         +-------------------+                |
|         | HTLC Chaincode    |                |
|         | (Go: Lock/Claim/   |                |
|         | Refund/State)     |                |
|         +-------------------+                |
+---------------------------------------------+
```

**Off-chain gateway responsibility:** coordinate CLI/REST triggers, gather prompts, call the isolated LLM client, and relay responses while keeping payment verification hooks ready for the HTLC workflow.

**On-chain ledger responsibility:** enforce determinism via Fabric peers, hold HTLC contract state, validate pre-images, and ensure funds move only when cryptographic locks and timelocks satisfy policy.

See `docs/blockchain_architecture.md` for Fabric-specific guidance and `docs/offchain_architecture.md` for the Python ecosystem details.
