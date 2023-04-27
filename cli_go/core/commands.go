package core

import (
	"encoding/json"

	"github.com/charmbracelet/log"
	"github.com/robocorp/robo/cli/environment"
	"github.com/robocorp/robo/cli/process"
)

type Task struct {
	Name string
	Docs string
	File string
	Line int
}

func ListTasks(env environment.Environment) []Task {
	env.Variables["RC_LOG_OUTPUT_STDOUT"] = "1"

	proc := process.New("python", "-m", "robo", "list", "tasks.py")
	proc.Env = env.Variables

	output, err := proc.Run()
	if err != nil {
		log.Fatalf("Failed to read tasks: %v", output.Stderr)
	}

	var tasks []Task
	err = json.Unmarshal([]byte(output.Stdout), &tasks)
	if err != nil {
		log.Fatal(err)
	}

	return tasks
}

func RunTask(env environment.Environment, name string) {
	env.Variables["RC_LOG_OUTPUT_STDOUT"] = "1"

	proc := process.New("python", "-m", "robo", "run", "tasks.py", "-t", name)
	proc.Env = env.Variables
	proc.StdoutListener = func(line string) {
		log.Infof("Event: %v", line)
	}

	_, err := proc.Run()
	if err != nil {
		log.Fatalf("Failed to run task: %v", err)
	}
}
