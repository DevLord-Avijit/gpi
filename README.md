# FAKE CURRENCY - GPI

A small side project that simulates a digital wallet experience with a fake currency. This is purely for learning and fun — not real money or financial infrastructure. Use it to experiment with front-end dashboards, API design, and playful payment flows.

---

## Key features

- Add, send, and receive fake money
- View current balance and transaction history
- Simple session/local-storage based user simulation (no real auth required)
- Responsive dashboard for desktop and mobile
- Simple payment animations and micro-interactions on the frontend
- Optional fake QR payment flow and leaderboard for mock social features

---

## Project purpose

This repo is intended for:

- Practicing API design and frontend-backend wiring
- Building a playful simulation of wallet flows
- Learning how to display, animate, and persist transaction data
- Sharing a harmless “feel rich” toy with friends

---

## Installation (quick)

- Clone the repo: `git clone https://github.com/yourusername/fake-upi.git` then `cd fake-upi`
- Install dependencies:
  - Python/Flask: `pip install -r requirements.txt`
  - Node/Express + frontend: `npm install`
- Start app:
  - Flask: `python app.py` (default port 5000)
  - Node: `npm start` (default port 3000)
- Open browser at `http://localhost:5000` or `http://localhost:3000` depending on chosen stack.

---

## Authentication

Authentication is optional by design. The project supports two modes:

- Local mode: browser localStorage stores a lightweight "user" object (default for quick demos)
- Session mode: simple session cookie for dev convenience (no passwords, no real accounts)

If you want proper auth, add JWT or OAuth as a follow-up.

---

## API — routes & endpoints

All endpoints are under the `/api` prefix. Replace hostname and port as needed.

### 1) Get current balance
- Method: GET
- URL: /api/balance
- Description: Returns the current fake balance for the active user/session
- Example response: {"balance": 10000}

### 2) Add money (top-up fake wallet)
- Method: POST
- URL: /api/add
- Request body: {"amount": 500}
- Description: Adds amount to the current user's fake balance. Returns updated balance and a transaction record
- Example response: {"success": true, "balance": 10500, "transaction": {"type": "add", "amount": 500, "time": "2025-10-22T21:00:00"}}

### 3) Send money to another user
- Method: POST
- URL: /api/send
- Request body: {"recipient": "user2", "amount": 200, "note": "for chai"}
- Description: Deducts amount from sender and adds to recipient. Returns updated balance and transaction object
- Example response: {"success": true, "balance": 10300, "transaction": {"type": "send", "to": "user2", "amount": 200, "time": "2025-10-22T21:00:00"}}

### 4) Transaction history
- Method: GET
- URL: /api/transactions
- Query params (optional): ?limit=20&skip=0
- Description: Returns chronological list of transactions for active user
- Example response: [{"type":"send","to":"user2","amount":200,"time":"2025-10-22T21:00:00"}, {"type":"add","amount":500,"time":"2025-10-22T20:45:00"}]

### 5) User list / basic user management (dev-only)
- Method: GET
- URL: /api/users
- Description: Returns list of fake users (id, displayName, mockUPI)
- Example response: [{"id":"user1","name":"Avijit","upi":"avijit@fake"}, {"id":"user2","name":"Riya","upi":"riya@fake"}]
- Method: POST
- URL: /api/users
- Request body: {"name":"NewUser","upi":"new@fake"}
- Description: Create a new demo user (no real auth)

### 6) Generate fake QR for payment
- Method: GET
- URL: /api/qr?user=user1&amount=100
- Description: Returns a URL or payload representing a fake QR (for front-end to render)
- Example response: {"qrPayload":"upi://pay?pa=user1@fake&pn=User1&am=100"}

### 7) Resolve QR / pay via QR
- Method: POST
- URL: /api/qr/pay
- Request body: {"qrPayload":"...", "payer":"user3"}
- Description: Simulate scanning & paying a QR; moves fake balance between accounts and returns transaction details
- Example response: {"success": true, "transaction": {...}, "balance": 9700}

### 8) Admin / leaderboard (optional)
- Method: GET
- URL: /api/leaderboard
- Description: Returns sorted list of users by fake balance
- Example response: [{"id":"user10","name":"Richie","balance":1000000}, ...]

### 9) Health / ping
- Method: GET
- URL: /api/health
- Description: Basic health check for deployment/monitoring
- Example response: {"status":"ok","uptime":"12h"}

---

## Data model (simple)

**User**
- id (string)
- name (string)
- upi (string) — fake handle for display
- balance (number)

**Transaction**
- id (string)
- type (add | send | receive)
- from (string | null)
- to (string | null)
- amount (number)
- note (string | null)
- time (ISO-8601 string)

Store in-memory for quick demo or persist to JSON/SQLite/low-cost DB for realistic sessions.

---

## Frontend expectations

- Dashboard: shows current balance, recent transactions, and quick actions (Add, Send, QR)
- Mobile and desktop responsive layouts
- Animations: success tick, floating money, confetti, balance increment
- Forms: Add money, Send money, QR pay modal
- Local demo mode: frontend can run with mockData and localStorage

---

## Use cases

- Learning: practice React/Vue/Svelte + backend API integration
- Prototyping: test wallet-style UX flows without real money
- Fun: generate funny screenshots of big balances
- Teaching: illustrate transactions, idempotency, and validation

---

## Validation & safety

- Always validate incoming amount server-side: positive integer, reasonable limits
- Prevent negative balances on send
- Add idempotency for retries (request IDs)
- Non-production: do not store or transmit real financial data

---

## Suggested endpoints to add later

- /api/refund — simulate reversing a transaction
- /api/notifications — mock push notifications
- /api/settings — user preferences (display currency, dark mode)
- /api/export — export transactions as CSV
- /api/webhooks — allow demo services to listen to fake events

---

## Examples (plain)

- Check balance: GET /api/balance → {"balance": 10000}
- Add money: POST /api/add with {"amount": 500} → updated balance + transaction
- Send money: POST /api/send with {"recipient":"user2","amount":200,"note":"movie"} → updated balance + transaction
- View history: GET /api/transactions?limit=10 → array of transactions

---

## Future ideas

- Fake QR scanning UI
- Leaderboard, achievements
- Multiple currencies & exchange rates
- Minimal social feed of payments (anonymized)
- Dark mode and polished micro-interactions

---

## License & disclaimers

- Open source for educational and entertainment use only
- Do not impersonate real payment systems
- No warranties — toy app

---

## Contact / contributions

Made for fun and learning. Contributions welcome via PRs. Keep it playful and harmless. Improvements like API docs tables, Postman collections, or example clients can be added.
