[![Donate](https://img.shields.io/badge/-%E2%99%A5%20Donate-%23ff69b4)](https://hmlendea.go.ro/fund.html) [![Latest GitHub release](https://img.shields.io/github/v/release/hmlendea/profi-bot)](https://github.com/hmlendea/profi-bot/releases/latest)

# About

This is a Python script that interacts with the **Profi** mobile app ecosystem. Profi is a Romanian market store chain. This bot allows users to **scan a Profi QR code** (from a store checkout) and **register the purchase** to their account — just like the official app does — to earn cashback.

Based on [whos-gabi/ProfiAppAPI-Exploit](https://github.com/whos-gabi/ProfiAppAPI-Exploit).

---

## ⚙️ Features

- 📷 Scans QR codes printed at Profi checkout registers
- 🔐 Registers the purchase to your Profi account
- 💸 Earns cashback as if scanned through the official app
- 🐧 Works on Linux devices, including phones where the official app isn't available

---

## 🚀 Getting Started

1. **Clone the repo**:
   ```bash
   git clone https://github.com/hmlendea/profi-bot.git
   cd profi-bot
   ```

2. **Install the requirements**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**:
   Edit `config.json`

4. **Run the script**:
   ```bash
   python main.py
   ```

---

## ⚠️ Disclaimer

> This tool interacts with the Profi ecosystem in a way that is **technically against their Terms of Service (ToS)**. It is not intended as an exploit or to generate cashback from receipts that don’t belong to you.
>
> This project is strictly for:
> - **Educational purposes**
> - **Personal use only**, especially on devices where the official Profi app cannot be used (e.g., Linux-based phones)

Using this tool for anything other than personal testing or when the official app is unusable may violate Profi’s policies and is **strongly discouraged**.

---

## ❤️ Support

If you find this project helpful, consider [donating here](https://hmlendea.go.ro/fund.html).

---

## 📄 License

Licensed under the [GPL-3.0](./LICENSE) License.
