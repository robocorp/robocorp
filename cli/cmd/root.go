package cmd

import (
	"os"

	"github.com/robocorp/robo/cli/fatal"
	"github.com/spf13/cobra"
)

var (
	verboseFlag bool
	directory   string
)

var rootCmd = &cobra.Command{
	Version: "v0.0.1",
	Use:     "robo",
	Short:   "All-in-one Python automation framework",
}

func init() {
	rootCmd.PersistentFlags().
		BoolVarP(&verboseFlag, "verbose", "v", false, "verbose output")
	rootCmd.PersistentFlags().
		StringVar(&directory, "directory", "", "working directory for commands (defaults to current)")
}

func Execute() {
	setDirectoryDefault()

	if err := rootCmd.Execute(); err != nil {
		fatal.FatalError(err)
	}
}

func setDirectoryDefault() {
	if directory == "" {
		var err error
		directory, err = os.Getwd()
		if err != nil {
			fatal.FatalError(err)
		}
	}
}
