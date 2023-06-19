package lock

import (
	"fmt"
	"path"

	"github.com/robocorp/robo/cli/config"
	"github.com/robocorp/robo/cli/config/conda"
	"github.com/robocorp/robo/cli/config/robot"
	"github.com/robocorp/robo/cli/environment"
	"github.com/robocorp/robo/cli/tasks"
	"github.com/robocorp/robo/cli/ui"
)

const (
	condaFile = "conda.yaml"
	robotFile = "robot.yaml"
)

var (
	bold  = ui.DefaultStyles().Bold
	title = bold.Margin(1, 0)
)

func CreateLockFiles(dir string, force bool) ([]string, error) {
	condaPath := path.Join(dir, condaFile)
	robotPath := path.Join(dir, robotFile)

	cfg, err := config.FromPath(dir)
	if err != nil {
		return nil, err
	}

	robotTasks, err := parseTasks(cfg)
	if err != nil {
		return nil, err
	}

	condaYaml := conda.NewFromConfig(cfg)
	if err := condaYaml.SaveAs(condaPath, force); err != nil {
		return nil, err
	}

	robotYaml := robot.NewFromConfig(cfg)
	robotYaml.Conda = condaFile
	robotYaml.Tasks = robotTasks
	if err = robotYaml.SaveAs(robotPath, force); err != nil {
		return nil, err
	}

	// TODO: Convert to debug/verbose print

	fmt.Println(title.Render("Conda configuration"))
	fmt.Println(condaYaml.Pretty())

	fmt.Println(title.Render("Robot configuration"))
	fmt.Println(robotYaml.Pretty())

	var files = []string{condaPath, robotPath}
	return files, nil
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
