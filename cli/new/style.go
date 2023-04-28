package new

import (
	"github.com/charmbracelet/lipgloss"
	"github.com/robocorp/robo/cli/ui"
)

var (
	styles    = ui.DefaultStyles()
	margin    = lipgloss.NewStyle().Margin(1, 1)
	faintText = styles.Faint.Render
)

func section(name, value string) string {
	return lipgloss.NewStyle().MarginBottom(1).Render(
		styles.Faint.Render(name), styles.Bold.Render(value),
	)
}

func errorBox(err error) string {
	return styles.ErrorBox.Render(err.Error())
}
