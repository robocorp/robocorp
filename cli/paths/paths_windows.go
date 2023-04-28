//go:build windows
// +build windows

package paths

import (
	"os"
	"path"
	"strings"
)

var (
	ExeSuffix = []string{".com", ".exe", ".bat", ".cmd"}
)

func RoboHome() string {
	userHome, err := os.UserHomeDir()
	if err != nil {
		panic(err)
	}

	return path.Join(userHome, "AppData", "Local", "robocorp", "robo")
}

func FindExecutable(path, pathenv string) (string, error) {
	if strings.IndexAny(path, `:\/`) != -1 {
		return toExecutable(path)
	}
	if f, err := toExecutable(`.\` + path); err == nil {
		return f, nil
	}
	for _, dir := range strings.Split(pathenv, `;`) {
		if f, err := toExecutable(dir + `\` + path); err == nil {
			return f, nil
		}
	}
	return path, os.ErrNotExist
}

func toExecutable(path string) (string, error) {
	lower := strings.ToLower(path)
	for _, ext := range ExeSuffix {
		if strings.HasSuffix(lower, ext) {
			return path, isFile(path)
		}
	}
	for _, ext := range ExeSuffix {
		path := path + ext
		if err := isFile(path); err == nil {
			return path, nil
		}
	}
	return path, os.ErrNotExist
}

func isFile(path string) error {
	f, err := os.Stat(path)
	if err != nil {
		return err
	}
	if f.IsDir() {
		return os.ErrPermission
	}
	return nil
}
