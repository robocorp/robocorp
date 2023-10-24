package cmd

import (
	"os"

	"github.com/robocorp/robo/cli/exit"
	"github.com/spf13/cobra"
)

var (
	version     string = "unknown"
	verboseFlag bool
	directory   string
)

var rootCmd = &cobra.Command{
	Version: version,
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
		exit.FatalExit(err)
	}
}

func setDirectoryDefault() {
	if directory == "" {
		var err error
		directory, err = os.Getwd()
		if err != nil {
			exit.FatalExit(err)
		}
	}
}
