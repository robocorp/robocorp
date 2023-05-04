package fatal

import (
	"fmt"

	"github.com/charmbracelet/lipgloss"
	"github.com/robocorp/robo/cli/ui"
)

var (
	errorTitle = ui.DefaultStyles().ErrorTitle.Render
	padding    = lipgloss.NewStyle().Padding(1, 0).Render
)

type FatalExit struct {
	Code    int
	Message string
}

func FatalErrorf(format string, a ...any) {
	msg := padding(lipgloss.JoinVertical(
		lipgloss.Left,
		errorTitle("Error"),
		fmt.Sprintf(format, a...),
	))
	panic(FatalExit{Code: 1, Message: msg})
}

func FatalError(a any) {
	FatalErrorf("%v", a)
}
