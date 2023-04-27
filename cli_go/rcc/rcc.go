package rcc

import (
	"os"
	"path"

	"github.com/robocorp/robo/cli/include"
	"github.com/robocorp/robo/cli/paths"
)

var (
	Controller = "robo-cli"
	Executable = path.Join(paths.BinPath(), "rcc")
)

func Ensure() {
	// TODO: Fix this
	if _, err := os.Stat(Executable); err == nil {
		return
	}

	if err := include.CopyFile("bin/rcc", Executable, 0o755); err != nil {
		panic(err)
	}
}
