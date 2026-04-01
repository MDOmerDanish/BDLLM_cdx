package chaincode

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type HTLCContract struct {
	contractapi.Contract
}

type HTLC struct {
	ContractID string  `json:"contractID"`
	Sender     string  `json:"sender"`
	Receiver   string  `json:"receiver"`
	Amount     float64 `json:"amount"`
	HashLock   string  `json:"hashLock"`
	TimeLock   int64   `json:"timeLock"`
	Status     string  `json:"status"`
}

const (
	StatusLocked   = "LOCKED"
	StatusClaimed  = "CLAIMED"
	StatusRefunded = "REFUNDED"
)

func modifyBalance(ctx contractapi.TransactionContextInterface, userID string, amount float64) error {
	stub := ctx.GetStub()
	balanceKey := fmt.Sprintf("balance_%s", userID)

	balanceBytes, err := stub.GetState(balanceKey)
	if err != nil {
		return fmt.Errorf("failed to read balance for %s: %w", userID, err)
	}

	var balance float64
	if len(balanceBytes) > 0 {
		if err := json.Unmarshal(balanceBytes, &balance); err != nil {
			return fmt.Errorf("invalid balance format for %s: %w", userID, err)
		}
	}

	balance += amount

	newBalanceBytes, err := json.Marshal(balance)
	if err != nil {
		return fmt.Errorf("failed to marshal balance for %s: %w", userID, err)
	}

	if err := stub.PutState(balanceKey, newBalanceBytes); err != nil {
		return fmt.Errorf("failed to persist balance for %s: %w", userID, err)
	}

	return nil
}

func (c *HTLCContract) MintTokens(ctx contractapi.TransactionContextInterface, userID string, amount float64) error {
	return modifyBalance(ctx, userID, amount)
}

func (c *HTLCContract) CreateLock(ctx contractapi.TransactionContextInterface, contractID, sender, receiver string, amount float64, hashLock string, durationSeconds int64) error {
	stub := ctx.GetStub()

	existing, err := stub.GetState(contractID)
	if err != nil {
		return fmt.Errorf("failed to read HTLC %s: %w", contractID, err)
	}
	if len(existing) > 0 {
		return fmt.Errorf("htlc %s already exists", contractID)
	}

	senderBalanceBytes, err := stub.GetState(fmt.Sprintf("balance_%s", sender))
	if err != nil {
		return fmt.Errorf("failed to read sender balance: %w", err)
	}

	var senderBalance float64
	if len(senderBalanceBytes) > 0 {
		if err := json.Unmarshal(senderBalanceBytes, &senderBalance); err != nil {
			return fmt.Errorf("invalid sender balance format: %w", err)
		}
	}

	if senderBalance < amount {
		return fmt.Errorf("insufficient balance for %s", sender)
	}

	if err := modifyBalance(ctx, sender, -amount); err != nil {
		return fmt.Errorf("failed to deduct funds from %s: %w", sender, err)
	}

	txTimestamp, err := stub.GetTxTimestamp()
	if err != nil {
		return fmt.Errorf("failed to retrieve transaction timestamp: %w", err)
	}

	timeLock := txTimestamp.Seconds + durationSeconds

	htlc := &HTLC{
		ContractID: contractID,
		Sender:     sender,
		Receiver:   receiver,
		Amount:     amount,
		HashLock:   hashLock,
		TimeLock:   timeLock,
		Status:     StatusLocked,
	}

	assetBytes, err := json.Marshal(htlc)
	if err != nil {
		return fmt.Errorf("failed to marshal htlc: %w", err)
	}

	if err := stub.PutState(contractID, assetBytes); err != nil {
		return fmt.Errorf("failed to save htlc %s: %w", contractID, err)
	}

	return nil
}

func (c *HTLCContract) Claim(ctx contractapi.TransactionContextInterface, contractID, preimage string) error {
	stub := ctx.GetStub()

	assetBytes, err := stub.GetState(contractID)
	if err != nil {
		return fmt.Errorf("failed to read htlc %s: %w", contractID, err)
	}
	if len(assetBytes) == 0 {
		return fmt.Errorf("htlc %s does not exist", contractID)
	}

	var htlc HTLC
	if err := json.Unmarshal(assetBytes, &htlc); err != nil {
		return fmt.Errorf("invalid htlc payload %s: %w", contractID, err)
	}

	if htlc.Status != StatusLocked {
		return fmt.Errorf("htlc %s is not in locked state", contractID)
	}

	computed := sha256.Sum256([]byte(preimage))
	computedHash := hex.EncodeToString(computed[:])
	if computedHash != htlc.HashLock {
		return fmt.Errorf("preimage hash mismatch for %s", contractID)
	}

	if err := modifyBalance(ctx, htlc.Receiver, htlc.Amount); err != nil {
		return fmt.Errorf("failed to credit receiver %s: %w", htlc.Receiver, err)
	}

	htlc.Status = StatusClaimed
	updated, err := json.Marshal(htlc)
	if err != nil {
		return fmt.Errorf("failed to marshal claimed htlc %s: %w", contractID, err)
	}

	if err := stub.PutState(contractID, updated); err != nil {
		return fmt.Errorf("failed to persist claimed htlc %s: %w", contractID, err)
	}

	return nil
}

func (c *HTLCContract) Refund(ctx contractapi.TransactionContextInterface, contractID string) error {
	stub := ctx.GetStub()

	assetBytes, err := stub.GetState(contractID)
	if err != nil {
		return fmt.Errorf("failed to read htlc %s: %w", contractID, err)
	}
	if len(assetBytes) == 0 {
		return fmt.Errorf("htlc %s does not exist", contractID)
	}

	var htlc HTLC
	if err := json.Unmarshal(assetBytes, &htlc); err != nil {
		return fmt.Errorf("invalid htlc payload %s: %w", contractID, err)
	}

	if htlc.Status != StatusLocked {
		return fmt.Errorf("htlc %s cannot be refunded in state %s", contractID, htlc.Status)
	}

	txTimestamp, err := stub.GetTxTimestamp()
	if err != nil {
		return fmt.Errorf("failed to retrieve transaction timestamp: %w", err)
	}

	if txTimestamp.Seconds < htlc.TimeLock {
		return fmt.Errorf("htlc %s is still locked until %d", contractID, htlc.TimeLock)
	}

	if err := modifyBalance(ctx, htlc.Sender, htlc.Amount); err != nil {
		return fmt.Errorf("failed to refund sender %s: %w", htlc.Sender, err)
	}

	htlc.Status = StatusRefunded
	updated, err := json.Marshal(htlc)
	if err != nil {
		return fmt.Errorf("failed to marshal refunded htlc %s: %w", contractID, err)
	}

	if err := stub.PutState(contractID, updated); err != nil {
		return fmt.Errorf("failed to persist refunded htlc %s: %w", contractID, err)
	}

	return nil
}
