# QuickKeys
QuickKeys is a background macro utility that automates login workflows and program launches via customizable keyboard shortcuts. Press a hotkey combination (e.g., Ctrl + F10) to instantly paste credentials, launch applications with auto-fill, or simply open programs. All usernames and passwords are stored with encryption for security.
Security Notice: QuickKeys is provided as-is for personal use. While credentials are encrypted, users should evaluate their own security requirements. Not recommended for high-security enterprise environments. Use at your own risk.


# Encryption
Master password — The master password itself is never stored. Instead, a cryptographic salt and verification hash derived from the password are stored within the encrypted file header. When you enter your password, the app uses Argon2 (a secure password hashing algorithm) to verify it matches.
Keybind data — All your keybinds (including any usernames, passwords, custom text, program paths, etc.) are stored in keybinds.enc — an encrypted file using the cryptography library (Fernet symmetric encryption). The encryption key is derived from your master password.
Security — Without the correct master password, the keybinds.enc file cannot be decrypted. The data is protected at rest.
