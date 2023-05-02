package cmd

import (
	"github.com/robocorp/robo/cli/fatal"
	"github.com/robocorp/robo/cli/operations/new"
	"github.com/spf13/cobra"
)

func init() {
	rootCmd.AddCommand(newCmd)
}

var newCmd = &cobra.Command{
	Use:   "new",
	Short: "Create a new project",
	Run: func(cmd *cobra.Command, args []string) {
		if _, err := new.NewProgram().Run(); err != nil {
			fatal.FatalErrorf("Could not create project: %s", err)
		}
	},
}
