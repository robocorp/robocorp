package tasks

import (
	"encoding/json"
	"errors"

	"github.com/robocorp/robo/cli/environment"
	"github.com/robocorp/robo/cli/process"
	"github.com/robocorp/robo/cli/tasks/output"
)

type Task struct {
	Name string
	Docs string
	File string
	Line int
}

func List(env environment.Environment) ([]Task, error) {
	env.Variables["RC_LOG_OUTPUT_STDOUT"] = "1"

	cmd := ListCommand()
	exe := env.FindExecutable(cmd[0])

	proc := process.New(exe, cmd[1:]...)
	proc.Env = env.ToSlice()

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

func Run(env environment.Environment, name string) error {
	env.Variables["RC_LOG_OUTPUT_STDOUT"] = "1"

	cmd := RunCommand(name)
	exe := env.FindExecutable(cmd[0])

	proc := process.New(exe, cmd[1:]...)
	proc.Env = env.ToSlice()

	events := output.New()
	proc.StdoutListener = func(line string) {
		events.Parse(line)
	}

	if _, err := proc.Run(); err != nil {
		return err
	}

	return nil
}

func ListCommand() []string {
	return []string{"python", "-m", "robocorp.tasks", "list", "tasks.py"}
}

func RunCommand(name string) []string {
	return []string{"python", "-m", "robocorp.tasks", "run", "tasks.py", "-t", name}
}
