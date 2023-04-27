package robot

import (
	"os"

	"github.com/robocorp/robo/cli/config/pyproject"
	yaml "gopkg.in/yaml.v2"
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

func NewFromConfig(cfg pyproject.Robo) *RobotYaml {
	return &RobotYaml{
		Ignored:    []string{".gitignore"},
		Path:       []string{"."},
		Pythonpath: []string{"."},
		Artifacts:  getOutputPath(cfg),
	}
}

func (it *RobotYaml) SaveAs(path string) error {
	content, err := yaml.Marshal(it)
	if err != nil {
		return err
	}

	return os.WriteFile(path, content, 0o666)
}

func getOutputPath(cfg pyproject.Robo) string {
	if cfg.Output != "" {
		return cfg.Output
	} else {
		return "output"
	}
}
