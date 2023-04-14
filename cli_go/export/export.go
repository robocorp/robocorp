package export

import (
	"fmt"
	"github.com/robocorp/robo/cli/config/conda"
	"github.com/robocorp/robo/cli/config/pyproject"
	"github.com/robocorp/robo/cli/config/robot"
)

const (
	CondaPath = "conda.yaml"
	RobotPath = "robot.yaml"
)

func ExportConfigs() error {
	cfg, err := pyproject.LoadPath("pyproject.toml")
	if err != nil {
		return fmt.Errorf("Failed to load pyproject.toml: %v", err)
	}

	condaYaml := conda.NewFromConfig(*cfg)
	if err := condaYaml.SaveAs(CondaPath); err != nil {
		return fmt.Errorf("Failed to save conda.yaml: %v", err)
	}

	robotYaml := robot.NewFromConfig(*cfg)
	robotYaml.Conda = CondaPath
	if err = robotYaml.SaveAs(RobotPath); err != nil {
		return fmt.Errorf("Failed to save robot.yaml: %v", err)
	}

	return nil
}
