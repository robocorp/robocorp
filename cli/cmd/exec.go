package cmd

import (
	"os"

	"github.com/robocorp/robo/cli/fatal"
	"github.com/robocorp/robo/cli/operations/exec"
	"github.com/spf13/cobra"
)

var execCmd = &cobra.Command{
	Use:   "exec -- [command]",
	Short: "Run a command inside the project environment",
	Run: func(cmd *cobra.Command, args []string) {
		if len(args) == 0 {
			cmd.Help()
			os.Exit(1)
		}

		if err := exec.Exec(directory, args); err != nil {
			fatal.FatalError(err)
		}
	},
}

func init() {
	rootCmd.AddCommand(execCmd)
}
