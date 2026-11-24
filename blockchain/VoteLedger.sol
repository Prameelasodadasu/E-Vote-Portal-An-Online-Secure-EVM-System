// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0; // Use a recent Solidity version

/**
 * @title VoteLedger
 * @dev A simple contract to log vote events immutably on the blockchain.
 * It records *that* a vote happened, not *what* the vote was.
 */
contract VoteLedger {

    // Event to be emitted when a vote is recorded
    // 'indexed' allows filtering events by these parameters later
    event VoteRecorded(
        uint256 indexed electionId,
        string indexed voterHash // Using string for voter_hash from Django
    );

    // Address of the contract owner/deployer (optional, but good practice)
    address public owner;

    // Constructor runs once when the contract is deployed
    constructor() {
        owner = msg.sender; // Set the deployer as the owner
    }

    /**
     * @dev Records a vote event on the blockchain.
     * Can only be called by authorized addresses if needed (not implemented here for simplicity).
     * @param _electionId The ID of the election the vote belongs to.
     * @param _voterHash The unique (hashed) identifier of the voter.
     */
    function recordVote(uint256 _electionId, string memory _voterHash) public {
        // Optional: Add access control here if needed, e.g., only owner or specific addresses
        // require(msg.sender == owner, "Only owner can record votes");

        // Emit an event to log the vote information immutably
        emit VoteRecorded(_electionId, _voterHash);
    }

    // Optional: Add functions to retrieve vote count or other data if needed,
    // but primarily we rely on listening for the VoteRecorded event off-chain.
}