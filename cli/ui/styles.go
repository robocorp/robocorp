package ui

import (
	"github.com/charmbracelet/lipgloss"
)

var (
	ColorBlack        = lipgloss.ANSIColor(0)
	ColorRed          = lipgloss.ANSIColor(1)
	ColorGreen        = lipgloss.ANSIColor(2)
	ColorYellow       = lipgloss.ANSIColor(3)
	ColorBlue         = lipgloss.ANSIColor(4)
	ColorPurple       = lipgloss.ANSIColor(5)
	ColorCyan         = lipgloss.ANSIColor(6)
	ColorWhite        = lipgloss.ANSIColor(7)
	ColorBrightBlack  = lipgloss.ANSIColor(8)
	ColorBrightRed    = lipgloss.ANSIColor(9)
	ColorBrightGreen  = lipgloss.ANSIColor(10)
	ColorBrightYellow = lipgloss.ANSIColor(11)
	ColorBrightBlue   = lipgloss.ANSIColor(12)
	ColorBrightPurple = lipgloss.ANSIColor(13)
	ColorBrightCyan   = lipgloss.ANSIColor(14)
	ColorBrightWhite  = lipgloss.ANSIColor(15)
)

type Styles struct {
	Faint    lipgloss.Style
	Bold     lipgloss.Style
	ErrorBox lipgloss.Style
}

func DefaultStyles() (s Styles) {
	s.Faint = lipgloss.NewStyle().Faint(true)
	s.Bold = lipgloss.NewStyle().Bold(true)
	s.ErrorBox = lipgloss.NewStyle().
		Width(80).
		Padding(0, 1).
		Margin(1, 0).
		Border(lipgloss.RoundedBorder()).
		BorderForeground(ColorBrightRed)

	return
}
