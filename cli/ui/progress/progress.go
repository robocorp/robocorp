package progress

import (
	"github.com/charmbracelet/bubbles/progress"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/robocorp/robo/cli/ui"
)

const (
	maxWidth = 80
)

var (
	faintText = ui.DefaultStyles().Faint.Render
)

type ProgressEvent struct {
	Current int
	Total   int
	Message string
}

func (e ProgressEvent) Percent() float64 {
	if e.Total == 0 {
		return 0
	}

	return float64(e.Current) / float64(e.Total)
}

type ProgressDone struct{}

func makeDone() tea.Cmd {
	return func() tea.Msg {
		return ProgressDone{}
	}
}

type Model struct {
	ch          chan ProgressEvent
	events      []ProgressEvent
	progressBar progress.Model
}

func New() Model {
	progressBar := progress.New(progress.WithDefaultGradient())
	progressBar.SetPercent(0)

	ch := make(chan ProgressEvent)
	events := make([]ProgressEvent, 0)

	m := Model{
		ch:          ch,
		events:      events,
		progressBar: progressBar,
	}

	return m
}

func (m Model) lastEvent() *ProgressEvent {
	if len(m.events) > 0 {
		return &m.events[len(m.events)-1]
	} else {
		return nil
	}
}

func (m Model) EventChannel() chan ProgressEvent {
	return m.ch
}

func (m Model) PollEvents() tea.Cmd {
	return func() tea.Msg {
		return <-m.ch
	}
}

func (m Model) Percent() float64 {
	if last := m.lastEvent(); last != nil {
		return last.Percent()
	} else {
		return 0
	}
}

func (m Model) Message() string {
	if last := m.lastEvent(); last != nil {
		return last.Message
	} else {
		return ""
	}
}

func (m Model) Update(msg tea.Msg) (Model, tea.Cmd) {
	switch msg := msg.(type) {
	case ProgressEvent:
		m.events = append(m.events, msg)
		percent := msg.Percent()
		cmd := m.progressBar.SetPercent(percent)
		if percent == 1.0 {
			return m, tea.Batch(cmd, makeDone())
		} else {
			return m, tea.Batch(cmd, m.PollEvents())
		}
	case progress.FrameMsg:
		progressModel, cmd := m.progressBar.Update(msg)
		m.progressBar = progressModel.(progress.Model)
		return m, cmd
	case tea.WindowSizeMsg:
		m.progressBar.Width = msg.Width
		if m.progressBar.Width > maxWidth {
			m.progressBar.Width = maxWidth
		}
		return m, nil
	default:
		return m, nil
	}
}

func (m Model) View() string {
	bar := m.progressBar.View()
	if msg := m.Message(); msg != "" {
		bar += "\n" + faintText(msg)
	}
	return bar
}

func (m Model) ViewAs(percent float64) string {
	bar := m.progressBar.ViewAs(percent)
	if msg := m.Message(); msg != "" {
		bar += "\n" + faintText(msg)
	}
	return bar
}
