# Py-Account-Manager

An open-source lightweight desktopsecure password manager application with OTP support and dark mode interface.

## Features

- Secure password storage with encryption
- OTP (One-Time Password) support
- Dark mode interface
- Copy options for passwords and OTP codes
- Master password protection
- Modern and intuitive UI

## Installation

### Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)

### Windows Installation

1. Clone the repository:
```bash
git clone <repository-url> [https://github.com/luizpalmieri/py-account-manager.git]
cd password-manager
```

2. You have two options for running the installation commands:

#### Option 1: Using make.bat (Recommended for Windows)
```bash
# Install dependencies and setup
make.bat install

# Run the application
make.bat run

# Run tests
make.bat test

# See all available commands
make.bat help
```

#### Option 2: Using Make (Requires Chocolatey)
1. Install Chocolatey (Run in PowerShell as Administrator):
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

2. Install Make:
```powershell
choco install make
```

3. Then use make commands:
```bash
make install
make run
make test
```

### Unix/Linux/MacOS Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd password-manager
```

2. Use make commands:
```bash
make install
make run
make test
```

## Available Commands

Both `make` and `make.bat` support these commands:

| Command | Description |
|---------|-------------|
| `install` | Install dependencies in a virtual environment |
| `run` | Run the Password Manager application |
| `test` | Run unit tests |
| `clean` | Clean up generated files and virtual environment |
| `dev-install` | Install development dependencies |
| `lint` | Run linting checks |
| `format` | Format code using black |
| `coverage` | Run tests with coverage report |
| `backup` | Create a database backup |
| `help` | Show help message |

## Compilation to Executable

You can compile the application into a standalone executable that can be run without Python installed.

### Windows

1. Install dependencies if you haven't already:
```bash
make.bat install
```

2. Build the application:
```bash
# Build windowed application (recommended)
make.bat build

# Build with console for debugging
make.bat build-debug
```

The executable will be created in the `dist` folder:
- `dist/py-account-manager.exe` - Main application
- `dist/py-account-manager-debug.exe` - Debug version with console

### Unix/Linux/MacOS

1. Install dependencies if you haven't already:
```bash
make install
```

2. Build the application:
```bash
# Build windowed application (recommended)
make build

# Build with console for debugging
make build-debug
```

The executable will be created in the `dist` folder:
- `dist/py-account-manager` - Main application
- `dist/py-account-manager-debug` - Debug version with console

### Notes about Compilation

- The windowed version (`make build`) runs without a console window
- The debug version (`make build-debug`) shows a console with output
- First-time compilation might take a few minutes
- The executable includes all dependencies
- Database files are stored in the user's home directory
- Compiled size is typically 20-30MB due to included libraries

## Development

### Project Structure
```
password_manager/
├── src/
│   ├── database/
│   │   └── database_manager.py
│   └── gui/
│       ├── main_window.py
│       ├── widgets.py
│       └── styles.py
├── tests/
│   └── test_database.py
├── main.py
├── requirements.txt
├── Makefile
├── make.bat
└── README.md
```

### Database Access

The password manager uses SQLite for data storage. The database file (`passwords.db`) contains:

1. Configuration Table:
```sql
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
)
```
- Stores master password hash and encryption salt

2. Accounts Table:
```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    otp_secret TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```
- Stores encrypted account information
- Passwords and OTP secrets are encrypted using Fernet encryption
- Timestamps track creation and modification dates

### Security Notes

- The database file is encrypted using your master password
- Never share your `passwords.db` file or master password
- Keep regular backups of your database file
- The database can only be accessed with the correct master password

### Development Workflow

1. Install development dependencies:
```bash
# Windows
make.bat dev-install

# Unix
make dev-install
```

2. Format code before committing:
```bash
# Windows
make.bat format

# Unix
make format
```

3. Run linting checks:
```bash
# Windows
make.bat lint

# Unix
make lint
```

4. Run tests with coverage:
```bash
# Windows
make.bat coverage

# Unix
make coverage
```

## Troubleshooting

### Common Issues

1. **Virtual Environment Issues**
   - Run `make.bat clean` (Windows) or `make clean` (Unix)
   - Then run install again

2. **Database Access Issues**
   - Ensure you're using the correct master password
   - If database is corrupted, restore from backup

3. **Dependencies Issues**
   - Try running `make.bat clean` then `make.bat install`
   - Check Python version (3.8+ required)

### Getting Help

If you encounter any issues:
1. Check the troubleshooting section
2. Run with debug logging enabled
3. Check the issue tracker
4. Create a new issue with detailed information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Install development dependencies (`make.bat dev-install` or `make dev-install`)
4. Make your changes
5. Run tests and linting
6. Submit a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
