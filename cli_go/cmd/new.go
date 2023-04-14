package cmd

import (
	"fmt"
	"os"

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

		if _, err := new.New().Run(); err != nil {
			fmt.Printf("Could not create project: %s\n", err)
			os.Exit(1)
		}
	},
}
