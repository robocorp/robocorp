package rcc

import (
	"os"

	"github.com/robocorp/robo/cli/include"
	"github.com/robocorp/robo/cli/paths"
)

var (
	Controller = "robo-cli"
)

func Ensure() {
	// TODO: Fix this
	if _, err := os.Stat(paths.RccBin); err == nil {
		return
	}

	if err := include.CopyFile(paths.RccInclude, paths.RccBin, 0o755); err != nil {
		panic(err)
	}
}
