package exec

import (
	"errors"
	"fmt"
	"os"
	"os/exec"
	"strings"

	"github.com/robocorp/robo/cli/config/pyproject"
	"github.com/robocorp/robo/cli/environment"
	"github.com/robocorp/robo/cli/paths"
	"github.com/robocorp/robo/cli/ui"
)

var (
	bold = ui.DefaultStyles().Bold.Render
)

func Exec(args []string) error {
	if len(args) == 0 {
		return errors.New("No arguments given!")
	}

	cfg, err := pyproject.LoadPath("pyproject.toml")
	if err != nil {
		return err
	}

	env, err := environment.EnsureWithProgress(*cfg)
	if err != nil {
		return err
	}

	fmt.Println("\nRunning command: " + bold(strings.Join(args, " ")))

	// TODO: Move as part of Environment struct
	var exe string
	if pathvar, ok := env.Variables["PATH"]; ok {
		if f, err := paths.FindExecutable(args[0], pathvar); err == nil {
			exe = f
		}
	} else {
		exe = args[0]
	}

	cmd := exec.Command(exe, args[1:]...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Env = env.ToSlice()

	return cmd.Run()
}
