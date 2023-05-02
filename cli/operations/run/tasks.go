package run

import (
	"fmt"

	"github.com/robocorp/robo/cli/environment"
	"github.com/robocorp/robo/cli/tasks"
	"github.com/robocorp/robo/cli/ui"
)

func selectTask(env environment.Environment) (string, error) {
	options, err := tasks.ListTasks(env)
	if err != nil {
		return "", fmt.Errorf("Failed to read tasks:\n%v", err)
	}
	if len(options) == 0 {
		return "", fmt.Errorf("No tasks defined!")
	}

	if len(options) == 1 {
		return options[0].Name, nil
	}

	return selectInteractive(options)
}

func selectInteractive(options []tasks.Task) (string, error) {
	if !ui.Interactive {
		return "", fmt.Errorf("Unable to select task in non-interactive mode")
	}

	// TODO: Implement
	return "", nil
}
