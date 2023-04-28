package environment

import (
	"os"
	"strings"
)

func getEnvironment() map[string]string {
	env := make(map[string]string)
	for _, item := range os.Environ() {
		key, val := splitKeyValue(item)
		env[key] = val
	}
	return env
}

func splitKeyValue(item string) (key, value string) {
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
