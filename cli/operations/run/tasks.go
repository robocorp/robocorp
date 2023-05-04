package run

import (
	"errors"
	"fmt"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"

	"github.com/robocorp/robo/cli/environment"
	"github.com/robocorp/robo/cli/tasks"
	"github.com/robocorp/robo/cli/ui"
	"github.com/robocorp/robo/cli/ui/choice"
)

var (
	padding = lipgloss.NewStyle().Padding(1, 0).Render
)

func selectTask(env environment.Environment) (string, error) {
	items, err := tasks.List(env)
	if err != nil {
		return "", fmt.Errorf("Failed to read tasks:\n%v", err)
	}
	if len(items) == 0 {
		return "", fmt.Errorf("No tasks defined!")
	}

	if len(items) == 1 {
		return items[0].Name, nil
	}

	return selectInteractive(items)
}

func selectInteractive(items []tasks.Task) (string, error) {
	if !ui.Interactive {
		return "", fmt.Errorf("Unable to select task in non-interactive mode")
	}

	options := make([]choice.Option, len(items))
	for i, t := range items {
		options[i] = choice.Option{
			Title:       t.Name,
			Description: t.Docs,
		}
	}

	initialModel := model{
		list: choice.New("Select task", options),
	}

	m, err := tea.NewProgram(initialModel).Run()
	if err != nil {
		return "", err
	}

	result := m.(model)
	if result.Error != nil {
		return "", result.Error
	}

	return result.Task, nil
}

type model struct {
	Task  string
	Error error

	list choice.Model
}

func (m model) Init() tea.Cmd {
	return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		if msg.Type == tea.KeyCtrlC {
			m.Error = errors.New("Aborted by user")
			return m, tea.Quit
		}
	}

	var cmd tea.Cmd
	m.list, cmd = m.list.Update(msg)

	if o := m.list.SelectedOption(); o != nil {
		m.Task = o.Title
		return m, tea.Batch(cmd, tea.Quit)
	}

	return m, cmd
}

func (m model) View() string {
	if m.Task == "" {
		return padding(m.list.View())
	} else {
		return ""
	}
}
