package cmd

import (
	"github.com/charmbracelet/log"
	"github.com/robocorp/robo/cli/export"
	"github.com/spf13/cobra"
)

func init() {
	rootCmd.AddCommand(exportCmd)
}

var exportCmd = &cobra.Command{
	Use:   "export",
	Short: "Create `rcc` compatible configuration files",
	Run: func(cmd *cobra.Command, args []string) {
		if err := export.ExportConfigs(); err != nil {
			log.Fatal(err)
		}
	},
}
