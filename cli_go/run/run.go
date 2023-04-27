package run

import (
	"github.com/charmbracelet/log"
	"github.com/robocorp/robo/cli/config/pyproject"
	"github.com/robocorp/robo/cli/core"
	"github.com/robocorp/robo/cli/environment"
)

func RunTask(name string) {
	robo, err := pyproject.LoadPath("pyproject.toml")
	if err != nil {
		log.Fatalf("Failed to load pyproject.toml: %v", err)
	}

	env, err := environment.EnsureFromConfig(*robo, nil)
	if err != nil {
		log.Fatalf("Failed to create environment: %v", err)
	}

	tasks := core.ListTasks(env)
	if len(tasks) == 0 {
		log.Fatal("No tasks defined!")
	}

	if name == "" {
		name = tasks[0].Name
	}

	log.Infof("Running task: %v", name)
	core.RunTask(env, name)
}
