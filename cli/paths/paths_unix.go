//go:build !windows
// +build !windows

package paths

import (
	"os"
	"path"
	"strings"
)

var (
	RccInclude = "bin/rcc"
	RccBin = path.Join(BinPath(), "rcc")
)

func RoboHome() string {
	userHome, err := os.UserHomeDir()
	if err != nil {
		panic(err)
	}

	return path.Join(userHome, ".robocorp", "robo")
}

func FindExecutable(path, pathenv string) (string, error) {
	if strings.Contains(path, "/") {
		return toExecutable(path)
	}
	for _, dir := range strings.Split(pathenv, ":") {
		if dir == "" {
			dir = "."
		}
		if f, err := toExecutable(dir + "/" + path); err == nil {
			return f, nil
		}
	}
	return path, os.ErrNotExist
}

func toExecutable(file string) (string, error) {
	f, err := os.Stat(file)
	if err != nil {
		return file, err
	}
	if m := f.Mode(); !m.IsDir() && m&0111 != 0 {
		return file, nil
	}
	return file, os.ErrPermission
}
