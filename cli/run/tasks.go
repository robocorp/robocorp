package run

import (
	"fmt"

	"github.com/robocorp/robo/cli/core"
	"github.com/robocorp/robo/cli/environment"
)

func selectTask(env environment.Environment) (string, error) {
	tasks, err := core.ListTasks(env)
	if err != nil {
		return "", fmt.Errorf("Failed to read tasks:\n%v", err)
	}
	if len(tasks) == 0 {
		return "", fmt.Errorf("No tasks defined!")
	}

	if len(tasks) == 1 {
		return tasks[0].Name, nil
	}

	return selectInteractive(tasks)
}

func selectInteractive(tasks []core.Task) (string, error) {
	// TODO: Implement
	return "", nil
}
