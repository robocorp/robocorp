package environment

import (
	"errors"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"

	"github.com/robocorp/robo/cli/config/pyproject"
	"github.com/robocorp/robo/cli/rcc"
	"github.com/robocorp/robo/cli/ui"
	"github.com/robocorp/robo/cli/ui/progress"
)

var (
	faintText = ui.DefaultStyles().Faint.Render
	margin    = lipgloss.NewStyle().Padding(1, 0).Render
)

type EnvironmentMsg = *Environment

type model struct {
	Cfg   pyproject.Robo
	Env   *Environment
	Error error

	progress progress.Model
}

func EnsureWithProgress(cfg pyproject.Robo) (*Environment, error) {
	if env, ok := TryCache(cfg); ok {
		return &env, nil
	}

	initialModel := model{
		Cfg:      cfg,
		progress: progress.New(),
	}

	m, err := tea.NewProgram(initialModel).Run()
	if err != nil {
		return nil, err
	}

	result := m.(model)
	if result.Error != nil {
		return nil, result.Error
	}

	return result.Env, nil
}

func (m model) Init() tea.Cmd {
	ch := m.progress.EventChannel()
	onProgress := func(p *rcc.Progress) {
		ch <- progress.ProgressEvent{
			Current: p.Current,
			Total:   p.Total,
			Message: p.Message,
		}
	}

	ensureCmd := func() tea.Msg {
		env, err := Create(m.Cfg, onProgress)
		if err != nil {
			return ui.ErrorMsg(err)
		}
		return EnvironmentMsg(&env)
	}

	return tea.Batch(
		m.progress.PollEvents(),
		ensureCmd,
	)
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		if msg.Type == tea.KeyCtrlC {
			m.Error = errors.New("Aborted by user")
			return m, tea.Quit
		}
	case ui.ErrorMsg:
		m.Error = msg
		return m, tea.Quit
	case EnvironmentMsg:
		m.Env = msg
		return m, tea.Quit
	}

	var cmd tea.Cmd
	m.progress, cmd = m.progress.Update(msg)
	return m, cmd
}

func (m model) View() string {
	sections := []string{
		"Building environment",
	}

	if m.Env != nil {
		sections = append(sections,
			m.progress.ViewAs(1.0),
		)
	} else if m.Error != nil {
		sections = append(sections,
			m.progress.View(),
		)
	} else {
		sections = append(sections,
			m.progress.View(),
			faintText("\nPress ctrl-c to abort"),
		)
	}

	return margin(lipgloss.JoinVertical(lipgloss.Left, sections...))
}
