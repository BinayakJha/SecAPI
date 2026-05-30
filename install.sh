#!/bin/sh
# Universal installation script for SecAPI
set -e

echo "🔍 Detecting system environment..."

# 1. Check if Python is installed
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Error: Python 3 is required to install SecAPI."
    echo "Please install Python 3 and try again."
    exit 1
fi

# 2. Check for pipx (recommended for isolated CLI tools)
if command -v pipx >/dev/null 2>&1; then
    echo "📦 Found 'pipx'. Installing SecAPI in an isolated environment..."
    pipx install git+https://github.com/BinayakJha/SecAPI.git --force
elif command -v pip3 >/dev/null 2>&1; then
    echo "📦 Found 'pip3'. Installing SecAPI user-wide..."
    pip3 install --user git+https://github.com/BinayakJha/SecAPI.git --upgrade
elif command -v pip >/dev/null 2>&1; then
    echo "📦 Found 'pip'. Installing SecAPI user-wide..."
    pip install --user git+https://github.com/BinayakJha/SecAPI.git --upgrade
else
    echo "❌ Error: Neither 'pipx' nor 'pip3'/'pip' was found."
    echo "Please install pip or pipx to proceed with installation."
    exit 1
fi

# 3. Check if secapi command is available in PATH
if ! command -v secapi >/dev/null 2>&1; then
    echo "\n⚠️  Warning: 'secapi' command is not in your current shell PATH."
    
    # Detect shell configuration file
    case "$SHELL" in
        */zsh) SHELL_RC="$HOME/.zshrc" ;;
        */bash) SHELL_RC="$HOME/.bashrc" ;;
        *) SHELL_RC="$HOME/.profile" ;;
    esac
    
    # Identify path suffix based on OS
    if [ "$(uname)" = "Darwin" ]; then
        PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        USER_PATH="\$HOME/Library/Python/$PY_VERSION/bin"
    else
        USER_PATH="\$HOME/.local/bin"
    fi
    
    echo "To add it to your PATH, run the following command or append it to your $SHELL_RC:"
    echo "  export PATH=\"\$PATH:$USER_PATH\""
fi

echo "\n🚀 SecAPI has been installed successfully!"
echo "💡 Try running: secapi --help"
