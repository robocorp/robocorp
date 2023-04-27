package cmd

import (
	"github.com/robocorp/robo/cli/run"
	"github.com/spf13/cobra"
)

func init() {
	rootCmd.AddCommand(runCmd)
}

var runCmd = &cobra.Command{
	Use:   "run",
	Short: "Run a project task",
	Run: func(cmd *cobra.Command, args []string) {
		if err := run.RunTask(""); err != nil {
			fatalError(err)
		}
	},
}
