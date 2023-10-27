package tasks

import (
	"fmt"
	"os"

	toml "github.com/pelletier/go-toml/v2"
)

// TODO: Initial guess of future config structure, probably will change
// TODO: robocorp-log doesn't read these, but should
// TODO: PyPI dependencies can have multiple types (path, git, version, etc.)
// Should probably make a dependency declaration into a union of string and object,
// similar to Poetry
type TasksToml struct {
	Name        string            `toml:"name"`
	Description string            `toml:"description"`
	Readme      string            `toml:"readme"`
	Python      string            `toml:"python"`
	Output      string            `toml:"output"`
	Tasks       []string          `toml:"tasks"`
	Include     []string          `toml:"include"`
	PyPI        map[string]string `toml:"pypi"`
	CondaForge  map[string]string `toml:"conda-forge"`
	Logging     struct {
		DefaultFilterKind string `toml:"default-filter-kind"`
		Filters           []struct {
			Name string `toml:"name"`
			Kind string `toml:"Kind"`
		}
	} `toml:"logging"`
}

func LoadPath(name string) (TasksToml, error) {
	data, err := os.ReadFile(name)
	if err != nil {
		return TasksToml{}, fmt.Errorf("Failed to read tasks.toml: %v", err)
	}

	var config TasksToml
	err = toml.Unmarshal(data, &config)
	if err != nil {
		return TasksToml{}, fmt.Errorf("Malformed tasks.toml: %v", err)
	}

	return config, nil
}
