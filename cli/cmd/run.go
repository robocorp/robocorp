package cmd

import (
	"github.com/robocorp/robo/cli/fatal"
	"github.com/robocorp/robo/cli/operations/run"
	"github.com/spf13/cobra"
)

func init() {
	rootCmd.AddCommand(runCmd)
}

var runCmd = &cobra.Command{
	Use:   "run [task to run]",
	Short: "Run a project task",
	Args:  cobra.MatchAll(cobra.MaximumNArgs(1), cobra.OnlyValidArgs),
	Run: func(cmd *cobra.Command, args []string) {
		task := ""
		if len(args) > 0 {
			task = args[0]
		}

		if err := run.RunTask(task); err != nil {
			fatal.FatalError(err)
		}
	},
}
