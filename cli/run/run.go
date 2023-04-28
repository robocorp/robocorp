package run

import (
	"fmt"
	"os"

	"github.com/robocorp/robo/cli/config/pyproject"
	"github.com/robocorp/robo/cli/core"
	"github.com/robocorp/robo/cli/environment"
	"github.com/robocorp/robo/cli/ui"
)

var (
	bold = ui.DefaultStyles().Bold.Render
)

func RunTask(name string) error {
	cfg, err := pyproject.LoadPath("pyproject.toml")
	if err != nil {
		return err
	}

	env, err := environment.EnsureWithProgress(*cfg)
	if err != nil {
		return err
	}

	if name == "" {
		name, err = selectTask(*env)
		if err != nil {
			return err
		}
	}

	if err := clearOutput(*cfg); err != nil {
		return err
	}

	fmt.Println("\nRunning task: " + bold(name))
	return core.RunTask(*env, name)
}

func clearOutput(cfg pyproject.Robo) error {
	// TODO: Move default to sane place
	output := cfg.Output
	if output == "" {
		output = "output"
	}

	if err := os.RemoveAll(output); err != nil {
		return err
	}
	if err := os.MkdirAll(output, 0o755); err != nil {
		return err
	}

	return nil
}
