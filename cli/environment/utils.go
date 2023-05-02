package environment

import (
	"os"
	"strings"
)

func environ() map[string]string {
	env := make(map[string]string)
	for _, item := range os.Environ() {
		key, val := splitVar(item)
		env[key] = val
	}
	return env
}

func splitVar(item string) (key, value string) {
	x := strings.SplitN(item, "=", 2)
	switch len(x) {
	case 0:
		return "", ""
	case 1:
		return x[0], ""
	case 2:
		return x[0], x[1]
	}
	panic("unreachable")
}
