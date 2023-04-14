package new

import (
	"github.com/charmbracelet/bubbles/list"
)

const (
	listTitleHeight = 3 // Not directly inspectable from list bubble
)

type listItem struct {
	title, desc string
}

func (i listItem) Title() string       { return i.title }
func (i listItem) Description() string { return i.desc }
func (i listItem) FilterValue() string { return i.title }

func listRenderHeight(count int) int {
	d := list.NewDefaultDelegate()
	return count*(d.Height()+d.Spacing()) + listTitleHeight
}
