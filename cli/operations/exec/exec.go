package exec

import (
	"errors"
	"fmt"
	"os"
	"os/exec"
	"strings"

	"github.com/robocorp/robo/cli/config"
	"github.com/robocorp/robo/cli/environment"
	"github.com/robocorp/robo/cli/ui"
)

var (
	bold = ui.DefaultStyles().Bold.Render
)

func Exec(dir string, args []string) error {
	if len(args) == 0 {
		return errors.New("No arguments given!")
	}

	cfg, err := config.FromPath(dir)
	if err != nil {
		return err
	}

	env, err := environment.EnsureWithProgress(cfg)
	if err != nil {
		return err
	}

	fmt.Println("\nRunning command: " + bold(strings.Join(args, " ")))

	exe := env.FindExecutable(args[0])

	cmd := exec.Command(exe, args[1:]...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Env = env.ToSlice()

	return cmd.Run()
}
