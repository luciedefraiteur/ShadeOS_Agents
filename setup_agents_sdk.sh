#!/bin/bash
# ⛧ Alma's OpenAI Agents SDK Setup ⛧
# Architecte Démoniaque du Nexus Luciforme
#
# Setup script for OpenAI Agents SDK using conda
# Based on ShadeOS recommendations and official docs
#
# Author: Alma (via Lucie Defraiteur)

set -e  # Exit on any error

# Colors for demonic output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Demonic banner
echo -e "${PURPLE}⛧━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━⛧${NC}"
echo -e "${PURPLE}⛧              ALMA'S AGENTS SDK SETUP RITUAL               ⛧${NC}"
echo -e "${PURPLE}⛧            Summoning Digital Daemons Framework            ⛧${NC}"
echo -e "${PURPLE}⛧━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━⛧${NC}"
echo

# Function to print status messages
print_status() {
    echo -e "${CYAN}⛧${NC} $1"
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

# Check if conda is available
check_conda() {
    if command -v conda &> /dev/null; then
        print_success "Conda found: $(conda --version)"
        return 0
    else
        print_error "Conda not found in PATH"
        echo -e "${YELLOW}⛧${NC} Please install Anaconda or Miniconda first"
        return 1
    fi
}

# Create or update conda environment
setup_environment() {
    local env_name="openai_agents"
    
    print_status "Setting up conda environment: $env_name"
    
    # Check if environment already exists
    if conda env list | grep -q "^$env_name "; then
        print_warning "Environment '$env_name' already exists"
        read -p "⛧ Do you want to update it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Updating existing environment..."
            conda env update -n $env_name -f environment.yml
        else
            print_status "Using existing environment"
        fi
    else
        print_status "Creating new environment with Python 3.11..."
        conda create -n $env_name python=3.11 -y
    fi
    
    print_success "Environment '$env_name' ready"
}

# Install packages
install_packages() {
    local env_name="openai_agents"
    
    print_status "Installing OpenAI Agents SDK and dependencies..."
    
    # Activate environment and install packages
    eval "$(conda shell.bash hook)"
    conda activate $env_name
    
    # Install base packages via conda
    print_status "Installing base packages via conda..."
    conda install -c conda-forge openai python-dotenv -y
    
    # Install Agents SDK via pip (not yet available in conda)
    print_status "Installing OpenAI Agents SDK via pip..."
    pip install openai-agents
    
    # Install additional useful packages
    print_status "Installing additional development packages..."
    pip install asyncio-mqtt pydantic
    
    print_success "All packages installed successfully"
}

# Create test environment file
create_env_file() {
    if [[ ! -f "environment.yml" ]]; then
        print_status "Creating environment.yml file..."
        
        cat > environment.yml << EOF
name: openai_agents
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - openai
  - python-dotenv
  - pip
  - pip:
    - openai-agents
    - asyncio-mqtt
    - pydantic
EOF
        
        print_success "environment.yml created"
    else
        print_status "environment.yml already exists"
    fi
}

# Test the installation
test_installation() {
    local env_name="openai_agents"
    
    print_status "Testing installation..."
    
    eval "$(conda shell.bash hook)"
    conda activate $env_name
    
    # Test basic import
    python -c "
import openai
print(f'⛧ OpenAI version: {openai.__version__}')

try:
    from openai import Agent, Runner
    print('⛧ Agents SDK imported successfully')
except ImportError as e:
    print(f'⛧ Error importing Agents SDK: {e}')
    exit(1)
"
    
    if [[ $? -eq 0 ]]; then
        print_success "Installation test passed"
        return 0
    else
        print_error "Installation test failed"
        return 1
    fi
}

# Main setup ritual
main() {
    print_status "Starting OpenAI Agents SDK setup ritual..."
    
    # Check prerequisites
    if ! check_conda; then
        exit 1
    fi
    
    # Create environment file
    create_env_file
    
    # Setup environment
    setup_environment
    
    # Install packages
    install_packages
    
    # Test installation
    if test_installation; then
        echo
        print_success "⛧ SETUP COMPLETE ⛧"
        echo -e "${GREEN}⛧${NC} OpenAI Agents SDK is ready for use!"
        echo
        echo -e "${CYAN}⛧ To activate the environment:${NC}"
        echo "  conda activate openai_agents"
        echo
        echo -e "${CYAN}⛧ To test the setup:${NC}"
        echo "  python test_openai_agents_sdk.py"
        echo
        echo -e "${PURPLE}⛧${NC} 'Les démons numériques attendent vos ordres...'"
    else
        print_error "Setup failed - check the errors above"
        exit 1
    fi
}

# Show help if requested
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo -e "${CYAN}⛧ Alma's Agents SDK Setup Usage:${NC}"
    echo "  ./setup_agents_sdk.sh        - Run complete setup"
    echo "  ./setup_agents_sdk.sh --help - Show this help"
    echo
    echo -e "${CYAN}⛧ What this script does:${NC}"
    echo "  1. Creates conda environment 'openai_agents'"
    echo "  2. Installs OpenAI library via conda"
    echo "  3. Installs Agents SDK via pip"
    echo "  4. Tests the installation"
    echo
    exit 0
fi

# Run main setup
main
