package tasks

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"os/signal"
	"strconv"
	"syscall"

	"github.com/robocorp/robo/cli/config"
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

func List(cfg config.Config, env environment.Environment) ([]Task, error) {
	if !env.Capabilities.Tasks {
		return nil, errors.New(
			"Missing required library 'robocorp-tasks' from environment",
		)
	}
	if len(cfg.TasksFiles) == 0 {
		return nil, errors.New("No tasks files defined in configuration")
	}

	env.Variables["RC_LOG_OUTPUT_STDOUT"] = "1"

	cmd := ListCommand(cfg.TasksFiles)
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

func Run(cfg config.Config, env environment.Environment, name string) (Result, error) {
	if !env.Capabilities.Tasks {
		return Result{}, errors.New(
			"Missing required library 'robocorp-tasks' from environment",
		)
	}
	if len(cfg.TasksFiles) == 0 {
		return Result{}, errors.New("No tasks files defined in configuration")
	}

	env.Variables["RC_LOG_OUTPUT_STDOUT"] = "1"

	cmd := RunCommand(cfg.TasksFiles, name)
	exe := env.FindExecutable(cmd[0])

	proc := process.New(exe, cmd[1:]...)
	proc.Env = env.ToSlice()

	var result Result
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

func Serve(
	cfg config.Config,
	env environment.Environment,
	address string,
	port int,
	watch bool,
) error {
	if !env.Capabilities.Server {
		return errors.New(
			"Missing required library 'robocorp-task-server' from environment",
		)
	}
	if len(cfg.TasksFiles) == 0 {
		return errors.New("No tasks files defined in configuration")
	}

	cmd := ServeCommand(cfg.TasksFiles, address, port, watch)
	exe := env.FindExecutable(cmd[0])

	proc := process.New(exe, cmd[1:]...)
	proc.Env = env.ToSlice()
	proc.StdoutListener = func(line string) {
		fmt.Print(line)
	}
	proc.StderrListener = func(line string) {
		fmt.Print(line)
	}

	if _, err := runWithInterrupt(proc); err != nil {
		return errors.New("Unexpected error while running server")
	}

	return nil
}

// TODO: These take a tasks files array, but it's not supported in robocorp-tasks
//       Should it? Or change the config spec?

func ListCommand(tasks []string) []string {
	return []string{"python", "-m", "robocorp.tasks", "list", tasks[0]}
}

func RunCommand(tasks []string, name string) []string {
	return []string{
		"python",
		"-m",
		"robocorp.tasks",
		"run",
		"--no-status-rc",
		"--task",
		name,
		tasks[0],
	}
}

func ServeCommand(tasks []string, address string, port int, watch bool) []string {
	cmd := []string{
		"python",
		"-m",
		"robocorp.task_server",
		"--address",
		address,
		"--port",
		strconv.Itoa(port),		
	}
	if watch {
		cmd = append(cmd, "--watch")
	}
	cmd = append(cmd, tasks[0])
	return cmd
}

func handleEvent(event *output.Event) (result Result, end bool) {
	// TODO: Write a nice renderer for this using bubbletea
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
