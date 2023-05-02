package ui

import (
	"os"

	"github.com/mattn/go-isatty"
)

var (
	Interactive = true
)

func init() {
	stdin := isatty.IsTerminal(os.Stdin.Fd())
	stdout := isatty.IsTerminal(os.Stdout.Fd())
	stderr := isatty.IsTerminal(os.Stderr.Fd())
	Interactive = stdin && stdout && stderr
}
