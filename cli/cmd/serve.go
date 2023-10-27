package cmd

import (
	"github.com/robocorp/robo/cli/exit"
	"github.com/robocorp/robo/cli/operations/serve"
	"github.com/spf13/cobra"
)

var (
	serverAddress string
	serverPort    int
	serverWatch   bool
)

var serveCmd = &cobra.Command{
	Use:   "serve",
	Short: "Serve tasks as local API",
	Run: func(cmd *cobra.Command, args []string) {
		if err := serve.Serve(directory, serverAddress, serverPort, serverWatch); err != nil {
			exit.FatalExit(err)
		}
	},
}

func init() {
	serveCmd.Flags().
		StringVarP(&serverAddress, "address", "a", "localhost", "server address")
	serveCmd.Flags().
		IntVarP(&serverPort, "port", "p", 8080, "server port")
	serveCmd.Flags().
		BoolVarP(&serverWatch, "watch", "w", false, "automatically reload tasks")
	rootCmd.AddCommand(serveCmd)
}
