#! /bin/bash -e

# Save current directory and change to the script's directory.
pushd . > /dev/null
cd $(dirname $0)
venvDir=venv  # better to not clash in naming with Poetry's ".venv" default name

# Check first if we aren't sourcing the script instead of executing it, as sourcing
# will activate the environment instead.
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then  # it's sourced, not executed
    echo "Activating an already existing virtual environment."
    . ../$venvDir/bin/activate
    popd > /dev/null
    return  # stops the rest of the execution without exiting the shell
fi

# Get RCC, binary with which we're going to create the master environment.
if [ ! -f rcc ]; then
    system=$(uname -s)
    case ${system} in
        Linux*)     url=https://downloads.robocorp.com/rcc/releases/latest/linux64/rcc;;
        Darwin*)    url=https://downloads.robocorp.com/rcc/releases/latest/macos64/rcc;;
        *)           echo "Invalid platform '$system' detected!"; exit 1;
    esac
    curl -o rcc $url
    chmod +x rcc
fi

# Create a new or replace an already existing virtual environment.
cd ..  # place/check the new/existing venv in the devtools root dir
if [ -d $venvDir ]; then
    echo "Detected existing development environment."
    read -r -p "Do you want to create a clean environment? [Y/N] " response
    if [[ "$response" =~ ^[Yy] ]]; then
        echo "Replacing existing environment with a clean one..."
        newEnv=true
    else
        echo "Using existing development environment."
        newEnv=false
    fi
else
    echo "Creating a new environment..."
    newEnv=true
fi

if $newEnv; then
    ./bin/rcc venv development-environment.yaml --space robocorp-development --force
fi
. ./$venvDir/bin/activate  # environment already exists at this point
# Install requirements all the time (due to updates).
python -m pip install -Ur requirements.txt

# Start VS Code over the repo to open the entire project for development.
code .. || echo "VSCode binary not available in PATH! (skip opening)"

# Bring back the initial working directory.
popd > /dev/null

echo "Source the development script to activate the environment, example:"
echo "$ source $0"
