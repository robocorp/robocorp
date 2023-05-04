package main

import (
	"fmt"
	"os"

	"github.com/robocorp/robo/cli/cmd"
	"github.com/robocorp/robo/cli/fatal"
	"github.com/robocorp/robo/cli/paths"
)

func handleFatal() {
	if r := recover(); r != nil {
		if f, ok := r.(fatal.FatalExit); ok {
			fmt.Println(f.Message)
			os.Exit(f.Code)
		}
		panic(r)
	}
}

func main() {
	defer handleFatal()

	defer os.Stdout.Sync()
	defer os.Stderr.Sync()
	defer paths.CleanTempFiles()

	cmd.Execute()
}
