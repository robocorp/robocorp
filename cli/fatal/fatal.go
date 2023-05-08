package fatal

import (
	"fmt"

	"github.com/robocorp/robo/cli/ui"
)

var (
	errorTitle = ui.DefaultStyles().ErrorTitle.Render
)

type FatalExit struct {
	Code    int
	Message string
}

func FatalErrorf(format string, a ...any) {
	msg := "\n" + errorTitle("Error") + "\n\n" + fmt.Sprintf(format, a...)
	panic(FatalExit{Code: 1, Message: msg})
}

func FatalError(a any) {
	FatalErrorf("%v", a)
}
