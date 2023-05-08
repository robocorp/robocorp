package conda

import (
	"bytes"
	"fmt"
	"os"
	"sort"

	"github.com/robocorp/robo/cli/config"
	"github.com/robocorp/robo/cli/paths"
	yaml "gopkg.in/yaml.v3"
)

type CondaYaml struct {
	Name         string        `yaml:"name,omitempty"`
	Channels     []string      `yaml:"channels"`
	Dependencies []interface{} `yaml:"dependencies"`
	Prefix       string        `yaml:"prefix,omitempty"`
	PostInstall  []string      `yaml:"rccPostInstall,omitempty"`
}

func NewFromConfig(cfg config.Config) CondaYaml {
	pipDependencies := generatePipDependencies(cfg)
	return CondaYaml{
		Channels: cfg.Channels,
		Dependencies: []interface{}{
			fmt.Sprintf("python=%v", cfg.PythonVersion),
			fmt.Sprintf("pip=%v", cfg.PipVersion),
			map[string][]string{
				"pip": pipDependencies,
			},
		},
	}
}

func (it CondaYaml) Encode() ([]byte, error) {
	var b bytes.Buffer
	e := yaml.NewEncoder(&b)
	e.SetIndent(2)

	if err := e.Encode(it); err != nil {
		return nil, err
	}

	return b.Bytes(), nil
}

func (it CondaYaml) Pretty() string {
	if content, err := it.Encode(); err == nil {
		return string(content)
	} else {
		return fmt.Sprintf("%v", it)
	}
}

func (it *CondaYaml) SaveAs(path string, force bool) error {
	exists, err := paths.Exists(path)
	if err != nil {
		return err
	}

	if exists && !force {
		return fmt.Errorf("File already exists: %v", path)
	}

	content, err := it.Encode()
	if err != nil {
		return err
	}

	return os.WriteFile(path, content, 0o666)
}

func generatePipDependencies(cfg config.Config) []string {
	rows := make([]string, 0)
	for k, v := range cfg.Dependencies {
		if v == "*" {
			rows = append(rows, k)
		} else {
			rows = append(rows, fmt.Sprintf("%v==%v", k, v))
		}
	}
	sort.Strings(rows)
	return rows
}
