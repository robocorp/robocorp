package pyproject

import (
	"fmt"
	"os"

	toml "github.com/pelletier/go-toml/v2"
)

type PyprojectToml struct {
	Tool *Tool `toml:"tool"`
}

type Tool struct {
	Robo *Robo `toml:"robo"`
}

type Robo struct {
	Name            string            `toml:"name"`
	Description     string            `toml:"description"`
	Python          string            `toml:"python"`
	Output          string            `toml:"output"`
	Dependencies    map[string]string `toml:"dependencies"`
	DevDependencies map[string]string `toml:"dev-dependencies"`
}

func LoadPath(name string) (PyprojectToml, error) {
	data, err := os.ReadFile(name)
	if err != nil {
		return PyprojectToml{}, fmt.Errorf("Failed to read pyproject.toml: %v", err)
	}

	var config PyprojectToml
	err = toml.Unmarshal(data, &config)
	if err != nil {
		return PyprojectToml{}, fmt.Errorf("Malformed pyproject.toml: %v", err)
	}

	return config, nil
}
