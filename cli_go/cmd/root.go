package cmd

import (
	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Version: "v0.0.1",
	Use:     "robo",
	Short:   "All-in-one Python automation framework",
	Run: func(cmd *cobra.Command, args []string) {
		// TODO: Implement nicer help here
	},
}

func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		fatalError(err)
	}
}
