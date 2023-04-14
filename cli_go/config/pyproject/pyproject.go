package pyproject

import (
	toml "github.com/pelletier/go-toml/v2"
	"os"
)

type Root struct {
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

func LoadPath(path string) (*Robo, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	var root Root
	err = toml.Unmarshal(data, &root)
	if err != nil {
		return nil, err
	}

	return root.Tool.Robo, nil
}
