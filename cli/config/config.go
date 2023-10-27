package config

import (
	"errors"
	"fmt"
	"path"

	"github.com/robocorp/robo/cli/config/tasks"
	"github.com/robocorp/robo/cli/paths"
)


type PyPI struct {
	Dependencies map[string]string
}

type Conda struct {
	Dependencies map[string]string
	Channels     []string
}

type Config struct {
	Dir             string
	Name            string
	Description     string
	ReadmePath      string
	PythonVersion   string
	PipVersion      string
	OutputDir       string
	TasksFiles      []string
	IncludePatterns []string
	PyPI            PyPI
	Conda           Conda
}

func FromPath(root string) (Config, error) {
	toml, err := tasks.LoadPath(path.Join(root, "tasks.toml"))
	if err != nil {
		return Config{}, err
	}

	config := CreateDefaults()

	config.Dir = root
	config.Name = toml.Name  // TODO: Not used yet
	config.Description = toml.Description  // TODO: Not used yet
	config.ReadmePath = toml.Readme  // TODO: Not used yet
	config.PyPI.Dependencies = toml.PyPI
	config.Conda.Dependencies = toml.CondaForge
	config.Conda.Channels = []string{"conda-forge"}

	if (len(toml.Include) > 0) {
		config.IncludePatterns = toml.Include  // TODO: Not used yet
	}
	if (len(toml.Tasks) > 0) {
		config.TasksFiles = toml.Tasks
	}
	if toml.Python != "" {
		config.PythonVersion = toml.Python
	}

	if toml.Output != "" {
		config.OutputDir = path.Join(config.Dir, toml.Output)
		isChild, err := paths.IsChild(config.Dir, config.OutputDir)
		if err != nil {
			return Config{}, fmt.Errorf("Unable to parse output directory: %v", err)
		}
		if !isChild {
			return Config{}, errors.New("Output directory must be inside project")
		}
	}

	return config, nil
}

// TODO: Check these. Also, pip version probably will come from rcc eventually?
func CreateDefaults() Config {
	return Config{
		PythonVersion:   "3.9.13",
		PipVersion:      "22.1.2",
		OutputDir:       "output",
		TasksFiles:      []string{"tasks.py"},
		IncludePatterns: []string{"*.py"},
	}
}
