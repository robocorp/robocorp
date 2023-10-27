package environment

import (
	"github.com/robocorp/robo/cli/process"
)

type Capabilities struct {
	Tasks  bool
	Server bool
}

func probeCapabilities(env Environment) Capabilities {
	cap := Capabilities{false, false}

	pythonExe := env.FindExecutable("python")
	processEnv := env.ToSlice()

	proc := process.New(pythonExe, "-c", "import robocorp.tasks")
	proc.Env = processEnv
	if _, err := proc.Run(); err == nil {
		cap.Tasks = true
	}

	proc = process.New(pythonExe, "-c", "import robocorp.task_server")
	proc.Env = processEnv
	if _, err := proc.Run(); err == nil {
		cap.Server = true
	}

	return cap
}
