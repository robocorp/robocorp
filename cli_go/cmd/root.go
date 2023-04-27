package cmd

import (
	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Version: "v0.0.1",
	Use:     "robo",
	Short:   "All-in-one Python automation framework",
}

func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		fatalError(err)
	}
}
