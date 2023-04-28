package core

import (
	"encoding/json"
	"errors"

	"github.com/robocorp/robo/cli/environment"
	"github.com/robocorp/robo/cli/process"
)

type Task struct {
	Name string
	Docs string
	File string
	Line int
}

func ListTasks(env environment.Environment) ([]Task, error) {
	env.Variables["RC_LOG_OUTPUT_STDOUT"] = "1"

	proc := process.New("python", "-m", "robocorp.tasks", "list", "tasks.py")
	proc.Env = env.Variables

	output, err := proc.Run()
	if err != nil {
		return nil, errors.New(output.Stderr)
	}

	var tasks []Task
	if err := json.Unmarshal([]byte(output.Stdout), &tasks); err != nil {
		return nil, err
	}

	return tasks, nil
}

func RunTask(env environment.Environment, name string) error {
	env.Variables["RC_LOG_OUTPUT_STDOUT"] = "1"

	proc := process.New("python", "-m", "robocorp.tasks", "run", "tasks.py", "-t", name)
	proc.Env = env.Variables
	// proc.StdoutListener = func(line string) {
	// 	parseEvent(line)
	// }

	if output, err := proc.Run(); err != nil {
		return errors.New(output.Stderr)
	}

	return nil
}
