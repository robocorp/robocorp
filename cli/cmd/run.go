package cmd

import (
	"github.com/robocorp/robo/cli/exit"
	"github.com/robocorp/robo/cli/operations/run"
	"github.com/spf13/cobra"
)

var runCmd = &cobra.Command{
	Use:   "run [task to run]",
	Short: "Run a project task",
	Args:  cobra.MatchAll(cobra.MaximumNArgs(1), cobra.OnlyValidArgs),
	Run: func(cmd *cobra.Command, args []string) {
		task := ""
		if len(args) > 0 {
			task = args[0]
		}

		result, err := run.RunTask(directory, task)
		if err != nil {
			exit.FatalExit(err)
		}

		if !result.Status {
			exit.SafeExit(1)
		}
	},
}

func init() {
	rootCmd.AddCommand(runCmd)
}
