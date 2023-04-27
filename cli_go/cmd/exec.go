package cmd

import (
	"github.com/robocorp/robo/cli/exec"
	"github.com/robocorp/robo/cli/paths"
	"github.com/spf13/cobra"
)

func init() {
	rootCmd.AddCommand(execCmd)
}

var execCmd = &cobra.Command{
	Use:   "exec",
	Short: "Run a command inside the project environment",
	Run: func(cmd *cobra.Command, args []string) {
		defer paths.CleanTempFiles()

		if err := exec.Exec(args); err != nil {
			fatalError(err)
		}
	},
}
