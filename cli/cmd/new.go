package cmd

import (
	"github.com/robocorp/robo/cli/new"
	"github.com/robocorp/robo/cli/paths"
	"github.com/spf13/cobra"
)

func init() {
	rootCmd.AddCommand(newCmd)
}

var newCmd = &cobra.Command{
	Use:   "new",
	Short: "Create a new project",
	Run: func(cmd *cobra.Command, args []string) {
		defer paths.CleanTempFiles()

		if _, err := new.NewProgram().Run(); err != nil {
			fatalErrorf("Could not create project: %s", err)
		}
	},
}
