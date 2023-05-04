package config

import (
	"errors"
	"fmt"
	"path"

	"github.com/robocorp/robo/cli/config/pyproject"
	"github.com/robocorp/robo/cli/paths"
)

type Config struct {
	Dir             string
	Name            string
	Description     string
	PythonVersion   string
	PipVersion      string
	OutputDir       string
	Dependencies    map[string]string
	DevDependencies map[string]string
	Channels        []string
}

func FromPath(root string) (Config, error) {
	cfg, err := pyproject.LoadPath(path.Join(root, "pyproject.toml"))
	if err != nil {
		return Config{}, err
	}

	robo := cfg.Tool.Robo
	if robo == nil {
		return Config{}, errors.New("Missing 'tool.robo' section in pyproject.toml")
	}

	config := CreateDefaults()

	config.Dir = root
	config.Name = robo.Name
	config.Description = robo.Description
	config.Dependencies = robo.Dependencies
	config.DevDependencies = robo.DevDependencies

	if robo.Python != "" {
		config.PythonVersion = robo.Python
	}

	if robo.Output != "" {
		config.OutputDir = path.Join(config.Dir, robo.Output)
		isChild, err := paths.IsChild(config.Dir, config.OutputDir)
		if err != nil {
			return Config{}, fmt.Errorf("Unable to read output directory: %v", err)
		}
		if !isChild {
			return Config{}, errors.New("Output directory must be inside project")
		}
	}

	return config, nil
}

func CreateDefaults() Config {
	return Config{
		PythonVersion: "3.9.13",
		PipVersion:    "22.1.2",
		OutputDir:     "output",
		Channels:      []string{"conda-forge"},
	}
}
