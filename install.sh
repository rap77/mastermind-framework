#!/bin/bash
# MasterMind Framework - Universal Installer
# Works on Linux, macOS, and WSL

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/rap77/mastermind-framework.git"
INSTALL_DIR="${HOME}/.mastermind-framework"
BIN_DIR="${HOME}/.local/bin"

echo -e "${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     MasterMind Framework - Installer                     ║
║     AI-powered expert brains for software development     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Print with color
print_step() {
    echo -e "${BLUE}➜${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Step 1: Check dependencies
print_step "Checking system dependencies..."

MISSING_DEPS=()

if ! command_exists git; then
    MISSING_DEPS+=("git")
fi

if ! command_exists curl; then
    MISSING_DEPS+=("curl")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    print_error "Missing required dependencies: ${MISSING_DEPS[*]}"
    echo ""
    echo "Please install them first:"
    case $OS in
        linux)
            echo "  sudo apt install git curl  # Ubuntu/Debian"
            echo "  sudo yum install git curl  # Fedora/RHEL"
            ;;
        macos)
            echo "  brew install git curl"
            ;;
    esac
    exit 1
fi

print_success "Dependencies found"

# Step 2: Install uv (Python package manager)
print_step "Installing uv package manager..."

if command_exists uv; then
    print_success "uv already installed"
else
    print_step "Downloading uv installer..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    print_success "uv installed"

    # Add uv to PATH for this session
    export PATH="$HOME/.local/bin:$PATH"
fi

# Verify uv is in PATH
if ! command_exists uv; then
    print_error "uv not found in PATH"
    echo ""
    echo "Add this to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "Then run: source ~/.bashrc  # or source ~/.zshrc"
    exit 1
fi

# Step 3: Clone or update repository
print_step "Setting up MasterMind Framework..."

if [ -d "$INSTALL_DIR" ]; then
    print_step "Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull origin master
    print_success "Repository updated"
else
    print_step "Cloning repository..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    print_success "Repository cloned"
fi

# Step 4: Install Python 3.14+ via uv
print_step "Ensuring Python 3.14+ availability..."

PYTHON_VERSION=$(uv python find 3.14 2>/dev/null || echo "")

if [ -z "$PYTHON_VERSION" ]; then
    print_step "Python 3.14 not found, installing via uv..."
    uv python install 3.14
    PYTHON_VERSION=$(uv python find 3.14)
fi

print_success "Python 3.14 ready: $PYTHON_VERSION"

# Step 5: Install mastermind globally
print_step "Installing MasterMind Framework globally..."

cd "$INSTALL_DIR"
uv pip install --system -e .

# Step 6: Create symlinks in ~/.local/bin
print_step "Creating command symlinks..."

mkdir -p "$BIN_DIR"

# Create symlinks for mastermind and mm
ln -sf "$INSTALL_DIR/.venv/bin/mastermind" "$BIN_DIR/mastermind" 2>/dev/null || true
ln -sf "$INSTALL_DIR/.venv/bin/mm" "$BIN_DIR/mm" 2>/dev/null || true

# If uv --global installed, use that instead
if uv pip list --global | grep -q mastermind-framework; then
    # Get uv global bin directory
    UV_BIN=$(uv pip list --global 2>&1 | grep -oP '(?<=Will be installed in ).*' || echo "")
    if [ -n "$UV_BIN" ] && [ -d "$UV_BIN" ]; then
        ln -sf "$UV_BIN/mastermind" "$BIN_DIR/mastermind" 2>/dev/null || true
        ln -sf "$UV_BIN/mm" "$BIN_DIR/mm" 2>/dev/null || true
    fi
fi

print_success "Commands installed: mastermind, mm"

# Step 7: Update PATH if needed
print_step "Checking PATH configuration..."

BIN_IN_PATH=false

# Check if ~/.local/bin is in PATH
if echo ":$PATH:" | grep -q ":$HOME/.local/bin:"; then
    BIN_IN_PATH=true
    print_success "~/.local/bin already in PATH"
else
    print_warning "~/.local/bin not in PATH"

    # Detect shell
    SHELL_RC=""
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bashrc"
    fi

    if [ -n "$SHELL_RC" ]; then
        echo "" >> "$SHELL_RC"
        echo "# MasterMind Framework" >> "$SHELL_RC"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
        print_success "Added to $SHELL_RC"

        echo ""
        echo -e "${YELLOW}⚠ Run the following to complete installation:${NC}"
        echo "  source $SHELL_RC"
        echo ""
        echo "Or restart your terminal."
    else
        print_error "Could not detect shell config file"
        echo ""
        echo "Add this to your shell config (~/.bashrc or ~/.zshrc):"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
fi

# Step 8: Verify installation
if command_exists mm; then
    print_success "Installation complete!"
    echo ""
    echo -e "${CYAN}Available commands:${NC}"
    echo "  ${GREEN}mm${NC} info              - Show framework info"
    echo "  ${GREEN}mm${NC} install status     - Check installation status"
    echo "  ${GREEN}mm${NC} brain status       - Check brain status"
    echo ""
    echo -e "${CYAN}To use in a project:${NC}"
    echo "  cd /path/to/your-project"
    echo "  mm install init"
    echo ""
    echo -e "${CYAN}Documentation:${NC}"
    echo "  https://github.com/rap77/mastermind-framework"
else
    print_warning "Installation completed but 'mm' command not found in PATH"
    echo ""
    echo "Start a new terminal session or run:"
    if [ -n "$SHELL_RC" ]; then
        echo "  source $SHELL_RC"
    fi
fi

echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
