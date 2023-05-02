package main

import (
	"github.com/robocorp/robo/cli/cmd"
	"github.com/robocorp/robo/cli/paths"
)

func main() {
	defer paths.CleanTempFiles()

	cmd.Execute()
}
