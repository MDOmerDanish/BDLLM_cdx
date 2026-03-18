#!/usr/bin/env python3
import os
import subprocess
import sys


def setup_and_run_fabric():
    """Ensure Hyperledger Fabric network is up by running the provided setup script."""
    fabric_dir = os.path.join("blockchain", "fabric-samples")
    network_active = False

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
        # Docker not installed or command failed; treat as offline
        network_active = False

    if os.path.isdir(fabric_dir) and network_active:
        print("Fabric network appears to be already running.")
        return

    print("Fabric network not detected. Running setup_fabric.sh in the background...")
    try:
        subprocess.Popen(
            ["bash", os.path.join("blockchain", "setup_fabric.sh")],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        print("Started setup_fabric.sh (it may take a few minutes to complete).")
    except Exception as e:
        print(f"Failed to start setup_fabric.sh: {e}")


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


def main_menu():
    while True:
        print("\n=== Main Menu ===")
        print("1) Set up and Run Hyperledger Fabric Blockchain")
        print("2) LLM Server Registration")
        print("3) LLM User Registration")
        print("4) View system servers and users")
        print("5) Run Service")
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
        elif choice == "0":
            print("Exiting.")
            sys.exit(0)
        else:
            print("Invalid selection. Please choose a number from the menu.")


if __name__ == "__main__":
    main_menu()
