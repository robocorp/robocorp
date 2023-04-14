package cmd

import (
	"github.com/charmbracelet/log"
	"github.com/robocorp/robo/cli/export"
	"github.com/robocorp/robo/cli/rcc"
	"github.com/spf13/cobra"
)

func init() {
	rootCmd.AddCommand(deployCmd)
}

var deployCmd = &cobra.Command{
	Use:   "deploy",
	Short: "Deploy project to Control Room",
	Run: func(cmd *cobra.Command, args []string) {
		if err := export.ExportConfigs(); err != nil {
			log.Fatal(err)
		}
		if err := rcc.RobotWrap(); err != nil {
			log.Fatal(err)
		}
	},
}
