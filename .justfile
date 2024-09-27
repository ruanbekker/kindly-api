# Default target that shows help
default:
    @echo "Available commands:"
    @echo "  just build - Build Docker Containers"
    @echo "  just up    - Start Docker Compose in detached mode"
    @echo "  just down  - Stop Docker Compose and remove orphans"
    @echo "  just logs  - Tail Docker Compose logs"
    @echo ""
    @echo "Usage: just <command>"

# Build containers
build:
    docker compose build

# Start Docker Compose in detached mode
up:
    docker compose up --build -d

# Stop Docker Compose and remove orphans
down:
    docker compose down --remove-orphans

# Tail Docker Compose logs
logs:
    docker compose logs -f

