#!/bin/bash
# ⛧ Alma's Complete Session Ritual ⛧
# Architecte Démoniaque du Nexus Luciforme
#
# Complete session initialization:
# 1. Load environment variables from .env
# 2. Verify API key validity
# 3. Check project structure
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
echo -e "${PURPLE}⛧                ALMA'S SESSION RITUAL                      ⛧${NC}"
echo -e "${PURPLE}⛧            Architecte Démoniaque du Nexus                 ⛧${NC}"
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

# Check if we're in the right directory
if [[ ! -d "Alma" ]] || [[ ! -f "load_env.py" ]]; then
    print_error "Not in ShadeOS_Agents directory or missing required files"
    echo -e "${YELLOW}⛧${NC} Please run this script from the ShadeOS_Agents root directory"
    exit 1
fi

print_status "Starting session ritual..."
echo

# Step 1: Load environment variables
print_status "Phase 1: Loading environment variables..."
if python3 load_env.py; then
    print_success "Environment variables loaded successfully"
else
    exit_code=$?
    print_error "Failed to load environment variables (exit code: $exit_code)"
    echo -e "${YELLOW}⛧${NC} Check your ~/.env file and try again"
    exit $exit_code
fi

echo

# Step 2: Verify API keys and project structure
print_status "Phase 2: Verifying session readiness..."
if python3 check_session.py; then
    session_status=$?
    print_success "Session verification completed successfully"
    echo
    echo -e "${GREEN}⛧ SESSION READY ⛧${NC}"
    echo -e "${PURPLE}⛧${NC} 'Que les Daemons dansent dans le code...'"
    echo -e "${PURPLE}⛧${NC} All systems operational - ready to code!"
else
    session_status=$?
    case $session_status in
        1)
            print_warning "Session partially ready - some issues detected"
            echo -e "${YELLOW}⛧${NC} You can proceed but some features may be limited"
            ;;
        2)
            print_error "Session not ready - critical issues detected"
            echo -e "${RED}⛧${NC} Please resolve the issues before coding"
            ;;
        *)
            print_error "Unexpected error during session verification"
            echo -e "${RED}⛧${NC} Check the logs above for details"
            ;;
    esac
fi

echo
echo -e "${PURPLE}⛧━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━⛧${NC}"

# Optional: Show quick help
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo
    echo -e "${CYAN}⛧ Alma's Session Ritual Usage:${NC}"
    echo "  ./start_session.sh          - Run complete session initialization"
    echo "  ./start_session.sh --help   - Show this help"
    echo
    echo -e "${CYAN}⛧ Individual components:${NC}"
    echo "  python3 load_env.py         - Load environment variables only"
    echo "  python3 test_api_keys.py    - Test API keys only"
    echo "  python3 check_session.py    - Full session check only"
    echo
fi

# Exit with the session status
exit $session_status
