package cmd

import (
	"github.com/robocorp/robo/cli/fatal"
	"github.com/spf13/cobra"
)

var (
	Verbose = false
)

var rootCmd = &cobra.Command{
	Version: "v0.0.1",
	Use:     "robo",
	Short:   "All-in-one Python automation framework",
}

func init() {
	rootCmd.PersistentFlags().
		BoolVarP(&Verbose, "verbose", "v", false, "verbose output")
}

func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		fatal.FatalError(err)
	}
}
