package cmd

import (
	"github.com/robocorp/robo/cli/fatal"
	"github.com/robocorp/robo/cli/operations/exec"
	"github.com/spf13/cobra"
)

func init() {
	rootCmd.AddCommand(execCmd)
}

var execCmd = &cobra.Command{
	Use:   "exec",
	Short: "Run a command inside the project environment",
	Run: func(cmd *cobra.Command, args []string) {
		if err := exec.Exec(args); err != nil {
			fatal.FatalError(err)
		}
	},
}
