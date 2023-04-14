package exec

import (
	"fmt"
	"github.com/charmbracelet/log"
	"github.com/robocorp/robo/cli/config/pyproject"
	"github.com/robocorp/robo/cli/env"
	"os"
	"os/exec"
	"strings"
)

func Exec(args []string) {
	if len(args) == 0 {
		log.Fatal("No arguments given!")
	}

	robo, err := pyproject.LoadPath("pyproject.toml")
	if err != nil {
		log.Fatal(err)
	}

	env, err := env.EnsureFromConfig(*robo, nil)
	if err != nil {
		log.Fatal(err)
	}

	log.Info(fmt.Sprintf("Running command: %v", strings.Join(args, " ")))
	cmd := exec.Command(args[0], args[1:]...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Env = env.ToSlice()

	if err := cmd.Run(); err != nil {
		log.Fatal(err)
	}
}
