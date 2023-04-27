package export

import (
	"fmt"
	"os"

	"github.com/robocorp/robo/cli/config/conda"
	"github.com/robocorp/robo/cli/config/pyproject"
	"github.com/robocorp/robo/cli/config/robot"
	"github.com/robocorp/robo/cli/rcc"
)

const (
	CondaPath = "conda.yaml"
	RobotPath = "robot.yaml"
)

func ExportProject(path string, force bool) error {
	cfg, err := pyproject.LoadPath("pyproject.toml")
	if err != nil {
		return fmt.Errorf("Failed to load pyproject.toml: %v", err)
	}

	condaYaml := conda.NewFromConfig(*cfg)
	if err := condaYaml.SaveAs(CondaPath); err != nil {
		return fmt.Errorf("Failed to save conda.yaml: %v", err)
	}

	defer os.Remove(CondaPath)

	robotYaml := robot.NewFromConfig(*cfg)
	robotYaml.Conda = CondaPath
	if err = robotYaml.SaveAs(RobotPath); err != nil {
		return fmt.Errorf("Failed to save robot.yaml: %v", err)
	}

	defer os.Remove(RobotPath)

	if err := rcc.RobotWrap(path); err != nil {
		return fmt.Errorf("Failed to create zip file: %v", err)
	}

	return nil
}
