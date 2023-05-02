package fatal

import (
	"fmt"
	"os"

	"github.com/robocorp/robo/cli/ui"
)

var (
	errorBox = ui.DefaultStyles().ErrorBox.Render
)

func FatalErrorf(format string, a ...any) {
	msg := fmt.Sprintf(format, a...)
	fmt.Println(errorBox(msg))
	os.Exit(1)
}

func FatalError(a any) {
	FatalErrorf("%v", a)
}
