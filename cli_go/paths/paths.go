package paths

import (
	"os"
	"path"
)

var (
	tempFiles = make([]string, 0)
)

func BinPath() string {
	return path.Join(RoboHome(), "bin")
}

func CreateTempFile(dir string, pattern string) string {
	file, err := os.CreateTemp(dir, pattern)
	if err != nil {
		panic(err)
	}

	defer file.Close()
	name := file.Name()
	tempFiles = append(tempFiles, name)

	return name
}

func CleanTempFiles() {
	for _, f := range tempFiles {
		os.Remove(f)
	}
}
