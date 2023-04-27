package conda

import (
	"fmt"
	"os"
	"sort"

	"github.com/robocorp/robo/cli/config/pyproject"
	yaml "gopkg.in/yaml.v2"
)

const (
	defaultPythonVersion = "3.9.13"
	defaultPipVersion    = "22.1.2"
)

type CondaYaml struct {
	Name         string        `yaml:"name,omitempty"`
	Channels     []string      `yaml:"channels"`
	Dependencies []interface{} `yaml:"dependencies"`
	Prefix       string        `yaml:"prefix,omitempty"`
	PostInstall  []string      `yaml:"rccPostInstall,omitempty"`
}

func NewFromConfig(cfg pyproject.Robo) *CondaYaml {
	pipDependencies := generatePipDependencies(cfg)
	return &CondaYaml{
		Channels: getDefaultChannels(),
		Dependencies: []interface{}{
			fmt.Sprintf("python=%v", getPythonVersion(cfg)),
			fmt.Sprintf("pip=%v", defaultPipVersion),
			map[string][]string{
				"pip": pipDependencies,
			},
		},
	}
}

func (it *CondaYaml) SaveAs(path string) error {
	content, err := yaml.Marshal(it)
	if err != nil {
		return err
	}

	return os.WriteFile(path, content, 0o666)
}

func generatePipDependencies(cfg pyproject.Robo) []string {
	rows := make([]string, 0)
	for key, element := range cfg.Dependencies {
		rows = append(rows, fmt.Sprintf("%v==%v", key, element))
	}
	sort.Strings(rows)
	return rows
}

func getPythonVersion(cfg pyproject.Robo) string {
	if cfg.Python != "" {
		return cfg.Python
	} else {
		return "3.9.13"
	}
}

func getDefaultChannels() []string {
	return []string{"conda-forge"}
}
