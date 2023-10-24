package tasks

import (
	"encoding/json"
	"fmt"
	"os"
	"os/signal"
	"strconv"
	"syscall"

	"github.com/robocorp/robo/cli/environment"
	"github.com/robocorp/robo/cli/process"
	"github.com/robocorp/robo/cli/tasks/output"
	"github.com/robocorp/robo/cli/ui"
)

var (
	faintText = ui.DefaultStyles().Faint.Render
)

type Task struct {
	Name string
	Docs string
	File string
	Line int
}

type Result struct {
	Status bool
}

func List(env environment.Environment) ([]Task, error) {
	env.Variables["RC_LOG_OUTPUT_STDOUT"] = "1"

	cmd := ListCommand()
	exe := env.FindExecutable(cmd[0])

	proc := process.New(exe, cmd[1:]...)
	proc.Env = env.ToSlice()

	output, err := runWithInterrupt(proc)
	if err != nil {
		return nil, err
	}

	var tasks []Task
	if err := json.Unmarshal([]byte(output.Stdout), &tasks); err != nil {
		return nil, err
	}

	return tasks, nil
}

func Run(env environment.Environment, name string) (Result, error) {
	var result Result
	env.Variables["RC_LOG_OUTPUT_STDOUT"] = "1"

	cmd := RunCommand(name)
	exe := env.FindExecutable(cmd[0])

	proc := process.New(exe, cmd[1:]...)
	proc.Env = env.ToSlice()

	events := output.New()
	proc.StdoutListener = func(line string) {
		event, err := events.Parse(line)
		if err != nil {
			return
		}
		if res, end := handleEvent(event); end {
			result = res
		}
	}

	_, err := runWithInterrupt(proc)
	return result, err
}

func ListCommand() []string {
	return []string{"python", "-m", "robocorp.tasks", "list", "tasks.py"}
}

func RunCommand(name string) []string {
	return []string{
		"python",
		"-m",
		"robocorp.tasks",
		"run",
		"--no-status-rc",
		"--task",
		name,
		"tasks.py",
	}
}

func handleEvent(event *output.Event) (result Result, end bool) {
	switch event.Type {
	case output.EventTypeConsole:
		if event.Fields["kind"] == "stdout" {
			if msg, ok := event.Fields["message"].(string); ok {
				fmt.Print(faintText(msg))
			}
		}
	case output.EventTypeEndRun:
		end = true
		result.Status = event.Fields["status"] == "PASS"
		if result.Status {
			fmt.Println("\n✅ Run successful")
		} else {
			fmt.Println("\n❌ Run failed")
		}
	}
	return
}

func runWithInterrupt(proc *process.Process) (*process.Output, error) {
	signals := make(chan os.Signal, 1)
	defer signal.Reset(os.Interrupt, syscall.SIGTERM)
	defer close(signals)

	signal.Notify(signals, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-signals
		defer signal.Reset(os.Interrupt, syscall.SIGTERM)
	}()

	return proc.Run()
}
