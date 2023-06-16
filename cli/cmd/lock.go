package cmd

import (
	"github.com/robocorp/robo/cli/fatal"
	"github.com/robocorp/robo/cli/operations/lock"
	"github.com/spf13/cobra"
)

var lockCmd = &cobra.Command{
	Use:   "lock",
	Short: "Generate configuration files for Control Room",
	Run: func(cmd *cobra.Command, args []string) {
		if _, err := lock.CreateLockFiles(directory, forceFlag); err != nil {
			fatal.FatalError(err)
		}
	},
}

func init() {
	lockCmd.Flags().
		BoolVarP(&forceFlag, "force", "f", false, "overwrite existing configuration files")
	rootCmd.AddCommand(lockCmd)
}
