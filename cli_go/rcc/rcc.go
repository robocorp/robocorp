package rcc

import (
	"github.com/charmbracelet/log"
	"github.com/robocorp/robo/cli/include"
	"github.com/robocorp/robo/cli/paths"
	"os"
	"path"
)

var (
	Controller = "robo-cli"
	Executable = path.Join(paths.BinPath(), "rcc")
	logger     = log.NewWithOptions(os.Stderr, log.Options{Prefix: "rcc"})
)

func Ensure() {
	// TODO: Fix this
	if _, err := os.Stat(Executable); err == nil {
		return
	}

	logger.Info("Copying executable", "path", Executable)
	if err := include.CopyFile("bin/rcc", Executable, 0o755); err != nil {
		panic(err)
	}
}
