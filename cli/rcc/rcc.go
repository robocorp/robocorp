package rcc

import (
	"os"

	"github.com/robocorp/robo/cli/include"
	"github.com/robocorp/robo/cli/paths"
)

var (
	Controller = "robo-cli"
)

func Ensure() error {
	// TODO: Fix this
	if _, err := os.Stat(paths.RccBin); err == nil {
		return nil
	}

	return include.CopyFile(paths.RccInclude, paths.RccBin, 0o755)
}
