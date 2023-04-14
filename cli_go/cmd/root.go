package cmd

import (
	"github.com/charmbracelet/log"
	"github.com/spf13/cobra"
	//"github.com/spf13/viper"
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
		log.Fatal(err)
	}
}
