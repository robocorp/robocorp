package main

import (
	"fmt"
	"os"

	"github.com/robocorp/robo/cli/cmd"
	"github.com/robocorp/robo/cli/exit"
	"github.com/robocorp/robo/cli/paths"
	"github.com/robocorp/robo/cli/process"
	"github.com/robocorp/robo/cli/ui"
)

var (
	errorTitle = ui.DefaultStyles().ErrorTitle.Render
)

func handlePanic() {
	if r := recover(); r != nil {
		if f, ok := r.(exit.FatalError); ok {
			fmt.Println("\n\n" + errorTitle("Error") + "\n\n" + f.Message)
			os.Exit(f.Code)
		}
		panic(r)
	}
}

func main() {
	defer handlePanic()
	defer process.KillAll()

	defer os.Stdout.Sync()
	defer os.Stderr.Sync()
	defer paths.CleanTempFiles()

	cmd.Execute()
}
