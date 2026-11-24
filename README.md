# E-Vote-Portal-Online-Secure-EVM-System

This is a comprehensive E-Voting system built as a major project. It features a secure Django backend with a dynamic HTML/JavaScript frontend. The system ensures vote integrity and voter privacy through OTP authentication, end-to-end encryption, and a blockchain-based audit trail.

This project was built by **Kishore Reddy**, **Prameela**, and **Kavya**.

---

## ✨ Key Features

* **Secure Voter Frontend:** An attractive, user-friendly interface with animated backgrounds for login, OTP verification, and voting.
* **Real-time SMS OTP:** Authenticators voters using a one-time password sent via the **Twilio API**.
* **Secure Token Authentication:** Uses DRF Auth Tokens to secure the voting API, ensuring only verified users can vote once.
* **Vote Encryption:** All vote choices are **encrypted** (using `Fernet`) before being saved to the database, ensuring privacy.
* **Blockchain Audit Trail:** Every vote is recorded as an immutable transaction on a local **Ganache blockchain** (using `web3.py` and a Solidity contract).
* **AI Anomaly Detection:** Includes a simple AI check to detect and block rapid, bot-like voting patterns.
* **Data Science Logging:** Logs all votes to a CSV file (`data/vote_log.csv`) for analysis in a **Jupyter Notebook**.
* **Custom Admin Dashboard:** Uses `django-jazzmin` for a modern admin theme (with light/dark modes) and features a custom page with a **live vote tally bar chart** (using `Chart.js`).
* **Full Audit Trail:** Logs all key actions (OTP requests, votes, tally access) in the database.

---

## 🛠️ Tech Stack

* **Backend:** Python, Django, Django REST Framework
* **Frontend:** HTML5, CSS3, JavaScript (`fetch`, `particles.js`)
* **Database:** SQLite 3
* **Authentication:** `rest_framework.authtoken`, Twilio (SMS OTP), `passlib`
* **Encryption:** `cryptography` (Fernet)
* **Blockchain:** Solidity, Ganache, `web3.py`
* **Data/AI:** Pandas, Matplotlib, Jupyter Notebook
* **Admin:** `django-jazzmin`, `Chart.js`

---

## 🚀 How to Run

### 1. Prerequisites
* Python 3.10+
* Ganache
* A Twilio Account

### 2. Backend Setup
1.  Navigate into the `backend` folder: `cd backend`
2.  Create and activate a virtual environment:
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate
    ```
3.  Install all requirements:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Deploy Smart Contract
1.  Open the **Ganache** application.
2.  Open **Remix IDE** ([remix.ethereum.org](https://remix.ethereum.org/)).
3.  Paste the code from `blockchain/VoteLedger.sol` into a new file on Remix.
4.  Compile the contract.
5.  Deploy the contract to your Ganache (e.g., `http://127.0.0.1:7545`).
6.  Copy the **Contract Address** and **ABI**.

### 4. Configure Settings
1.  Open `backend/evm_portal/settings.py`.
2.  Fill in your secret keys:
    * `TWILIO_ACCOUNT_SID`
    * `TWILIO_AUTH_TOKEN`
    * `TWILIO_PHONE_NUMBER`
    * `VOTE_ENCRYPTION_KEY` (Generate one with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`)
    * `VOTE_LEDGER_CONTRACT_ADDRESS` (from Remix)
    * `VOTE_LEDGER_CONTRACT_ABI` (from Remix)

### 5. Run the System
1.  Run database migrations:
    ```bash
    python manage.py migrate
    ```
2.  Create your admin account:
    ```bash
    python manage.py createsuperuser
    ```
3.  **Run the server:**
    ```bash
    python manage.py runserver
    ```
4.  **Open the Frontend:** Open the `index.html` file (located in the root or `frontend` folder) in your web browser to start the voting process.
5.  **View Admin Panel:** Go to `http://127.0.0.1:8000/admin/` to log in as an admin, manage users/voters, and see the live tally chart.
   ### Outputs:**
   Here are the screenshots of the Voter Login Page and Dashboard Admin Panel.
    <img width="1918" height="823" alt="Screenshot 2025-10-23 081120" src="https://github.com/user-attachments/assets/92517d4a-fbdf-48c9-97d7-4988eaab6c0f" />
    <img width="1919" height="1010" alt="Screenshot 2025-10-23 081423" src="https://github.com/user-attachments/assets/bfaf3877-ac72-4e24-8073-a7dec1333bd0" />
    <img width="1919" height="997" alt="Screenshot 2025-10-23 081503" src="https://github.com/user-attachments/assets/38e7cfd8-b19e-42dc-8618-15948cc09238" />
    <img width="1917" height="1010" alt="Screenshot 2025-10-23 081546" src="https://github.com/user-attachments/assets/28e099b9-0c35-4612-ba91-d7f71b89389b" />
    <img width="1919" height="1012" alt="Screenshot 2025-10-23 081825" src="https://github.com/user-attachments/assets/e6c31dd5-b638-4f21-a26f-fb37795368fc" />
    <img width="1917" height="947" alt="Screenshot 2025-10-23 012317" src="https://github.com/user-attachments/assets/b5e80035-54c2-46a8-9283-8e5ab294c719" />

    


