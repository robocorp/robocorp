#!/bin/bash -e

# Save current directory and change to the script's directory
pushd . > /dev/null
scriptPath=$(dirname "$0")
cd "$scriptPath"

# Get RCC
if [ ! -f "./rcc" ]; then
    curl -o rcc https://downloads.robocorp.com/rcc/releases/latest/linux64/rcc
    chmod +x rcc
fi

# Go to repo root
cd ..

# Check if activate script exists
if [ -f "./venv" ]; then
    echo "Detected existing development environment."
    read -r -p "Do you want to create a clean environment? [Y/N] " response
    if [[ "$response" =~ ^[Yy] ]]; then
        echo "Creating a clean environment..."
        ./devutils/rcc venv devutils/dev-env-libraries.yaml -s dev-library-env --force
        ./venv/bin/activate
        pip install -Ur devutils/requirements.txt
    else
        echo "Using existing development environment."
        ./venv/bin/activate
    fi
fi

# Start VS Code
code .

popd > /dev/null
