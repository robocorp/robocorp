package robot

import (
	"bytes"
	"fmt"
	"os"

	"github.com/robocorp/robo/cli/config"
	"github.com/robocorp/robo/cli/paths"
	yaml "gopkg.in/yaml.v3"
)

type RobotYaml struct {
	Tasks        map[string]*Task `yaml:"tasks"`
	Devtasks     map[string]*Task `yaml:"devTasks"`
	Conda        string           `yaml:"condaConfigFile,omitempty"`
	PreRun       []string         `yaml:"preRunScripts,omitempty"`
	Environments []string         `yaml:"environmentConfigs,omitempty"`
	Ignored      []string         `yaml:"ignoreFiles"`
	Artifacts    string           `yaml:"artifactsDir"`
	Path         []string         `yaml:"PATH"`
	Pythonpath   []string         `yaml:"PYTHONPATH"`
}

type Task struct {
	Task    string   `yaml:"robotTaskName,omitempty"`
	Shell   string   `yaml:"shell,omitempty"`
	Command []string `yaml:"command,omitempty"`
}

func NewFromConfig(cfg config.Config) RobotYaml {
	return RobotYaml{
		Ignored:    []string{".gitignore"},
		Path:       []string{"."},
		Pythonpath: []string{"."},
		Artifacts:  cfg.OutputDir,
	}
}

func (it RobotYaml) Encode() ([]byte, error) {
	var b bytes.Buffer
	e := yaml.NewEncoder(&b)
	e.SetIndent(2)

	if err := e.Encode(it); err != nil {
		return nil, err
	}

	return b.Bytes(), nil
}

func (it RobotYaml) Pretty() string {
	if content, err := it.Encode(); err == nil {
		return string(content)
	} else {
		return fmt.Sprintf("%v", it)
	}
}

func (it *RobotYaml) SaveAs(path string, force bool) error {
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
