package cmd

import (
	"fmt"
	"os"

	"github.com/robocorp/robo/cli/ui"
)

var (
	errorBox = ui.DefaultStyles().ErrorBox.Render
)

func fatalErrorf(format string, a ...any) {
	msg := fmt.Sprintf(format, a...)
	fmt.Println(errorBox(msg))
	os.Exit(1)
}

func fatalError(a any) {
	fatalErrorf("%v", a)
}
