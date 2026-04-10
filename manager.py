#!/usr/bin/env python3
import os
import subprocess
import sys

from blockchain.gateway import HTLCManager


def setup_and_run_fabric():
    """Ensure Hyperledger Fabric network is deterministically rebuilt when needed."""
    fabric_dir = os.path.join("blockchain", "fabric-samples")
    recovery_required = False

    # Diagnostic check for specific peer container states
    try:
        docker_check = subprocess.run(
            [
                "docker",
                "ps",
                "-a",
                "--filter",
                "name=peer0.org1",
                "--format",
                "{{.Status}}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        status_output = docker_check.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        status_output = ""

    if "Up" in status_output:
        print("[Fabric Diagnostic] Active peer containers detected. Network is live and ready. Do not execute the setup script.")
        return
    if "Exited" in status_output or status_output == "":
        print("[Fabric Diagnostic] Network requires recovery. Executing deterministic rebuild in the foreground...")
        recovery_required = True

    # Check if Fabric docker containers are running
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=peer", "--filter", "name=orderer", "-q"],
            capture_output=True,
            text=True,
            check=True,
        )
        network_active = bool(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        network_active = False

    if os.path.isdir(fabric_dir) and network_active:
        print("Fabric network appears to be already running.")
        return

    if not recovery_required:
        print("[Fabric Diagnostic] Network requires recovery. Executing deterministic rebuild in the foreground...")
        recovery_required = True

    if recovery_required:
        try:
            subprocess.run(["bash", "./blockchain/setup_fabric.sh"], check=True)
        except subprocess.CalledProcessError as e:
            print("[Error] Fabric recovery failed. Please check Docker daemon.")


def llm_server_registration():
    print("Not implemented yet will be ready soon.")


def llm_user_registration():
    print("Not implemented yet will be ready soon.")


def view_system_servers_and_users():
    print("Not implemented yet will be ready soon.")


def run_service():
    server_id = input("Server ID: ").strip()
    user_id = input("User ID: ").strip()
    print("Not implemented yet will be ready soon.")


def deploy_chaincode():
    try:
        subprocess.run(["bash", "./blockchain/deploy_htlc.sh"], check=True)
        print("HTLC chaincode deployment completed.")
    except subprocess.CalledProcessError as e:
        print("[Error] Chaincode deployment failed. Check the Fabric network status.")


def execute_htlc_payment():
    import time

    gateway = HTLCManager()
    contract_id = "htlc_test_01"
    sender_id = "client_001"
    receiver_id = "server_001"

    while True:
        print("\n=== HTLC Demonstration Suite ===")
        print("1) Smooth Transaction (Happy Path)")
        print("2) Malicious Server (Guessing Attack)")
        print("3) Client Abort (Refund)")
        print("4) Double Spend (Insufficient Funds)")
        print("0) Return to Main Menu")
        test_choice = input("Select a scenario: ")

        if test_choice == "1":
            amount = 5.0
            lock_data = gateway.create_lock(amount, receiver_id)
            print(f"[HTLC] Generated hash: {lock_data['hash']}")
            gateway.submit_lock_to_chain(contract_id, sender_id, receiver_id, amount, lock_data["hash"], 3600)
            print("[HTLC] Provider is processing LLM inference to earn the preimage...")
            gateway.submit_claim_to_chain(contract_id, lock_data["preimage"], lock_data["preimage"])
        elif test_choice == "2":
            amount = 5.0
            lock_data = gateway.create_lock(amount, receiver_id)
            gateway.submit_lock_to_chain(contract_id, sender_id, receiver_id, amount, lock_data["hash"], 3600)
            print("[HTLC] ALERT: Malicious server attempting to guess the secret...")
            gateway.submit_claim_to_chain(contract_id, "malicious_fake_preimage_123", lock_data["preimage"])
        elif test_choice == "3":
            amount = 5.0
            lock_data = gateway.create_lock(amount, receiver_id)
            gateway.submit_lock_to_chain(contract_id, sender_id, receiver_id, amount, lock_data["hash"], 2)
            print("[HTLC] Server unresponsive. Waiting for 2-second timelock to expire...")
            time.sleep(3)
            gateway.submit_refund_to_chain(contract_id)
        elif test_choice == "4":
            amount = 9999.0
            lock_data = gateway.create_lock(amount, receiver_id)
            print("[HTLC] Client attempting to lock 9999.0 tokens...")
            gateway.submit_lock_to_chain(contract_id, sender_id, receiver_id, amount, lock_data["hash"], 3600)
        elif test_choice == "0":
            break
        else:
            print("Invalid selection.")


def manage_llm_server():
    while True:
        print("\n=== LLM Server Operations ===")
        print("1) Start Custom LLM Node (OPT-125M)")
        print("2) Send Test Prompt")
        print("3) Stop vLLM Server")
        print("0) Return to Main Menu")
        llm_choice = input("Select an option: " ).strip()

        if llm_choice == "1":
            try:
                print("Initializing vLLM server; please allow a few moments for the model weights to load...")
                subprocess.run(
                    ["bash", "./start_vllm.sh"],
                    cwd="llm_server",
                    check=True,
                )
                print("vLLM server startup sequence triggered.")
            except subprocess.CalledProcessError:
                print("[Error] Failed to start vLLM server. Check the script output for details.")
        elif llm_choice == "2":
            user_prompt = input("Enter prompt for Custom LLM Node: ")
            from llm_server.llm_client import query_llm

            response = query_llm(user_prompt)
            if response:
                print(f"[vLLM] {response}")
            else:
                print("[vLLM] No response received from the server.")
        elif llm_choice == "3":
            try:
                subprocess.run(
                    ["bash", "./stop_vllm.sh"],
                    cwd="llm_server",
                    check=True,
                )
            except subprocess.CalledProcessError:
                print("[Error] Failed to stop vLLM server. Check the script output for details.")
        elif llm_choice == "0":
            break
        else:
            print("Invalid selection.")


def main_menu():
    while True:
        print("\n=== Main Menu ===")
        print("1) Set up and Run Hyperledger Fabric Blockchain")
        print("2) LLM Server Registration")
        print("3) LLM User Registration")
        print("4) View system servers and users")
        print("5) Run Service")
        print("6) Make Payment [Server id: server_001, Client id: client_001, Amount: 5.0]")
        print("7) Deploy HTLC Smart Contract.")
        print("8) LLM Server Management")
        print("0) Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            setup_and_run_fabric()
        elif choice == "2":
            llm_server_registration()
        elif choice == "3":
            llm_user_registration()
        elif choice == "4":
            view_system_servers_and_users()
        elif choice == "5":
            run_service()
        elif choice == "6":
            execute_htlc_payment()
        elif choice == "7":
            deploy_chaincode()
        elif choice == "8":
            manage_llm_server()
        elif choice == "0":
            print("Exiting.")
            sys.exit(0)
        else:
            print("Invalid selection. Please choose a number from the menu.")


if __name__ == "__main__":
    main_menu()
