package cmd

import (
	"github.com/robocorp/robo/cli/fatal"
	"github.com/robocorp/robo/cli/operations/serve"
	"github.com/spf13/cobra"
)

var serveCmd = &cobra.Command{
	Use:   "serve",
	Short: "Serve tasks as local API",
	Run: func(cmd *cobra.Command, args []string) {
		if err := serve.Serve(directory); err != nil {
			fatal.FatalError(err)
		}
	},
}

func init() {
	rootCmd.AddCommand(serveCmd)
}
