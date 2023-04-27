package cmd

import (
	"fmt"

	"github.com/robocorp/robo/cli/export"
	"github.com/spf13/cobra"
)

const (
	robotZip = "robot.zip"
)

func init() {
	rootCmd.AddCommand(exportCmd)
}

var exportCmd = &cobra.Command{
	Use:   "export",
	Short: "Export project as .zip file",
	Run: func(cmd *cobra.Command, args []string) {
		if err := export.ExportProject(robotZip, false); err != nil {
			fatalError(err)
		}

		fmt.Printf("Created export: %v\n", robotZip)
	},
}
