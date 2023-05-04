package export

import (
	"fmt"
	"os"

	"github.com/robocorp/robo/cli/config"
	"github.com/robocorp/robo/cli/config/conda"
	"github.com/robocorp/robo/cli/config/robot"
	"github.com/robocorp/robo/cli/environment"
	"github.com/robocorp/robo/cli/rcc"
	"github.com/robocorp/robo/cli/tasks"
	"github.com/robocorp/robo/cli/ui"
)

const (
	CondaPath = "conda.yaml"
	RobotPath = "robot.yaml"
)

var (
	bold  = ui.DefaultStyles().Bold
	title = bold.Margin(1, 0)
)

func ExportProject(dir, zipFile string, force bool) error {
	cfg, err := config.FromPath(dir)
	if err != nil {
		return err
	}

	robotTasks, err := parseTasks(cfg)
	if err != nil {
		return err
	}

	condaYaml := conda.NewFromConfig(cfg)
	if err := condaYaml.SaveAs(CondaPath, force); err != nil {
		return err
	}

	defer os.Remove(CondaPath)

	robotYaml := robot.NewFromConfig(cfg)
	robotYaml.Conda = CondaPath
	robotYaml.Tasks = robotTasks
	if err = robotYaml.SaveAs(RobotPath, force); err != nil {
		return err
	}

	defer os.Remove(RobotPath)

	if err := rcc.RobotWrap(zipFile); err != nil {
		return fmt.Errorf("Failed to create zip file: %v", err)
	}

	// TODO: Convert to debug/verbose print

	fmt.Println(title.Render("Conda configuration"))
	fmt.Println(condaYaml.Pretty())

	fmt.Println(title.Render("Robot configuration"))
	fmt.Println(robotYaml.Pretty())

	fmt.Println(bold.Inline(true).Render("Created zipfile:"), zipFile)

	return nil
}

func parseTasks(cfg config.Config) (map[string]*robot.Task, error) {
	env, err := environment.EnsureWithProgress(cfg)
	if err != nil {
		return nil, err
	}

	items, err := tasks.List(env)
	if err != nil {
		return nil, fmt.Errorf("Failed to read tasks:\n%v", err)
	}

	cmds := make(map[string]*robot.Task, 0)
	for _, t := range items {
		cmd := tasks.RunCommand(t.Name)
		cmds[t.Name] = &robot.Task{Command: cmd}
	}

	return cmds, nil
}
