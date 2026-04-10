# BDLLM Technical Overview

BDLLM (Blockchain Distributed LLM Marketplace) couples a Python-driven CLI orchestrator with a Hyperledger Fabric HTLC chaincode so that inference requests, payments, and ledger state can be audited from prompt to payout.

## System Architecture: On-Chain vs. Off-Chain
```
+-----------------------------------------------------------------------------------+
| Off-Chain Components                                                              |
|  +------------------------------+  +--------------------------+  +-------------+ |
|  | Python Orchestrator           |->| LLM Client (HTTP)        |->| FastAPI     | |
|  | (manager.py menus & HTLC demo)|  | (llm_client/llm_client.py)|  | LLM Node    | |
|  | - Fabric / HTLC tooling      |  | - POST /generate         |  | (engine_server.py)         |
|  +------------------------------+  +--------------------------+  +-------------+ |
+-----------------------------------------------------------------------------------+
| On-Chain Components                                                               |
|  +-------------------------------+                                                |
|  | Hyperledger Fabric Test       |                                                |
|  | Network (blockchain/fabric-    |                                                |
|  | samples test-network, peers,   |                                                |
|  | orderer, CA, setup_fabric.sh)  |                                                |
|  +-------------------------------+                                                |
|              |                                                                    |
|              v                                                                    |
|         +-------------------------+                                              |
|         | HTLC Chaincode (Go:     |                                              |
|         | ModifyBalance, CreateLock|                                              |
|         | Claim, Refund, Mint)     |                                              |
|         +-------------------------+                                              |
+-----------------------------------------------------------------------------------+
```

- **Off-chain gateway responsibility:** `manager.py` drives the CLI, runs Fabric diagnostics, deploys HTLC chaincode, manages the vLLM node, and exercises the HTLC demonstration flows while the lightweight `llm_client` exchanges JSON prompts with the FastAPI OPT-125M node.
- **On-chain ledger responsibility:** The Fabric test network keeps consensus, and `chaincode/htlc.go` enforces deterministic escrow via `CreateLock`, `Claim`, `Refund`, and balance bookkeeping enforced by `modifyBalance` and the transaction timestamp.

Dive deeper in `docs/onchain_architecture.md` and `docs/offchain_architecture.md` for the detailed breakdowns referenced below.
