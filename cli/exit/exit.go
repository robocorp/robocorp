package exit

import (
	"fmt"
	"os"
)

type FatalError struct {
	Code    int
	Message string
}

func (err *FatalError) Error() string {
	return err.Message
}

func FatalExitf(format string, a ...any) {
	msg := fmt.Sprintf(format, a...)
	panic(FatalError{Code: 1, Message: msg})
}

func FatalExit(a any) {
	FatalExitf("%v", a)
}

func SafeExit(code int) {
	os.Exit(code)
}
