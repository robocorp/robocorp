package fatal

import (
	"fmt"
	"os"

	"github.com/charmbracelet/lipgloss"
	"github.com/robocorp/robo/cli/ui"
)

var (
	errorTitle = ui.DefaultStyles().ErrorTitle.Render
	padding    = lipgloss.NewStyle().Padding(1, 0).Render
)

func FatalErrorf(format string, a ...any) {
	msg := padding(lipgloss.JoinVertical(
		lipgloss.Left,
		errorTitle("Error"),
		fmt.Sprintf(format, a...),
	))
	fmt.Println(msg)
	os.Exit(1)
}

func FatalError(a any) {
	FatalErrorf("%v", a)
}
