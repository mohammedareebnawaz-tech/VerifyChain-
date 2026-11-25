# VerifyChain: Certificate Verification Using Blockchain

A mini project for **Foundation of Blockchain**.

Fake or edited certificates are hard to spot, and manual verification is slow. VerifyChain stores a fingerprint (hash) of every certificate on a blockchain. Anyone can then verify a certificate instantly, and any tampering is detected.

## Run it (one command)

You need Python 3.8 or newer. No extra packages are required.

```bash
python app.py
```

On Mac/Linux use `python3 app.py`. Your browser opens automatically at http://localhost:8000.

You can also just double-click `run.bat` (Windows) or run `./run.sh` (Mac/Linux).

## How it works

1. **Issue:** the college enters the student name, course, certificate ID and date.
2. **Hash:** SHA-256 turns those details into a unique fingerprint.
3. **Store:** the fingerprint goes into a new block. The block is mined with Proof of Work and linked to the previous block through its hash.
4. **Verify:** an employer enters the certificate details. The system recomputes the fingerprint and compares it with the one on the chain, then re-checks the whole chain. Result: **Valid**, **Fake**, or a **Tampered** warning.

## Blockchain concepts covered

- Cryptographic hashing (SHA-256)
- Blocks linked by the previous block's hash
- Proof of Work (a block hash must start with `000`)
- Immutability and tamper detection
- Genesis block

## Demo steps

1. Issue a certificate in section 1.
2. Verify it with the same details in section 2. The result is **VALID**.
3. Change one letter in the name and verify again. The result is **FAKE**.
4. Click **Demo: tamper with Block #1** in section 3. The chain turns red and shows which block was modified.
5. Click **Reset chain** to start again.

## Run the tests

```bash
python -m unittest test_blockchain -v
```

## Project structure

```
VerifyChain/
├── app.py                # blockchain logic + web server + web page
├── test_blockchain.py    # 6 unit tests
├── run.bat               # double-click launcher (Windows)
├── run.sh                # launcher (Mac/Linux)
├── docs/
│   ├── VerifyChain_A3_Poster.pdf    # A3 poster (print this one)
│   ├── VerifyChain_A3_Poster.jpg
│   ├── VerifyChain_A3_Poster.pptx   # editable poster
│   └── VerifyChain_Presentation.pptx  # 8-slide explanation deck
├── README.md
└── .gitignore
```

## Future scope

- Smart contracts on Ethereum for a public, decentralized chain
- QR code printed on each certificate for one-scan verification
- Multiple issuing institutions with digital signatures
- Storing only the certificate hash on chain, for student privacy

## Team

- Mohammed Areeb Nawaz (20241CSG0044)
- Mohammed Touheed (20241CSG0021)

Guide: Neha Seirah Biju
