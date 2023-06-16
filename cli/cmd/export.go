package cmd

import (
	"github.com/robocorp/robo/cli/fatal"
	"github.com/robocorp/robo/cli/operations/export"
	"github.com/spf13/cobra"
)

var (
	robotZip string
)

var exportCmd = &cobra.Command{
	Use:   "export",
	Short: "Export project as .zip file",
	Run: func(cmd *cobra.Command, args []string) {
		if err := export.ExportProject(directory, robotZip, forceFlag); err != nil {
			fatal.FatalError(err)
		}
	},
}

func init() {
	exportCmd.Flags().
		BoolVarP(&forceFlag, "force", "f", false, "overwrite existing configuration files")
	exportCmd.Flags().
		StringVarP(&robotZip, "output", "o", "robot.zip", "path to output file")
	rootCmd.AddCommand(exportCmd)
}
