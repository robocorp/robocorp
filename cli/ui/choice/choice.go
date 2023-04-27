package choice

import (
	"github.com/charmbracelet/bubbles/list"
	tea "github.com/charmbracelet/bubbletea"
)

const (
	listTitleHeight = 3 // Not directly inspectable from list bubble
)

type listItem struct {
	title, description string
}

func (i listItem) Title() string       { return i.title }
func (i listItem) Description() string { return i.description }
func (i listItem) FilterValue() string { return "" }

type Option struct {
	Title, Description string
}

type Model struct {
	selected *Option
	options  []Option
	child    list.Model
}

func New(title string, options []Option) Model {
	items := make([]list.Item, len(options))
	for i, o := range options {
		items[i] = listItem{o.Title, o.Description}
	}

	child := list.New(items, list.NewDefaultDelegate(), 0, 0)
	child.Title = title
	child.SetShowStatusBar(false)
	child.SetFilteringEnabled(false)
	child.SetShowHelp(false)

	m := Model{
		options: options,
		child:   child,
	}

	return m
}

func (m Model) Update(msg tea.Msg) (Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		if msg.Type == tea.KeyEnter {
			if i, ok := m.child.SelectedItem().(listItem); ok {
				m.selected = &Option{i.Title(), i.Description()}
				return m, nil
			}
		}
	case tea.WindowSizeMsg:
		m.child.SetSize(msg.Width, msg.Height)
		if h := m.listRenderHeight(); h < msg.Height {
			m.child.SetHeight(h)
		}
		return m, nil
	}

	var cmd tea.Cmd
	m.child, cmd = m.child.Update(msg)
	return m, cmd
}

func (m Model) View() string {
	return m.child.View()
}

func (m Model) SelectedOption() *Option {
	return m.selected
}

func (m Model) listRenderHeight() int {
	d := list.NewDefaultDelegate()
	return len(m.options)*(d.Height()+d.Spacing()) + listTitleHeight
}
