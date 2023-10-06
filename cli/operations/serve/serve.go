package serve

import (
	"os"

	"github.com/robocorp/robo/cli/config"
	"github.com/robocorp/robo/cli/environment"
	"github.com/robocorp/robo/cli/tasks"
	"github.com/robocorp/robo/cli/ui"
)

var (
	bold = ui.DefaultStyles().Bold.Render
)

func Serve(dir string) error {
	cfg, err := config.FromPath(dir)
	if err != nil {
		return err
	}

	env, err := environment.EnsureWithProgress(cfg)
	if err != nil {
		return err
	}

	if err := clearOutput(cfg); err != nil {
		return err
	}

	return tasks.Serve(env)
}

func clearOutput(cfg config.Config) error {
	if err := os.RemoveAll(cfg.OutputDir); err != nil {
		return err
	}
	if err := os.MkdirAll(cfg.OutputDir, 0o755); err != nil {
		return err
	}

	return nil
}
