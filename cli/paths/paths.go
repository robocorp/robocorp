package paths

import (
	"os"
	"path"
	"regexp"
	"strings"
)

var (
	tempFiles = make([]string, 0)

	invalidRunePattern = regexp.MustCompile(`[^\w\d-_ ]+`)
	whitespacePattern  = regexp.MustCompile(`\s+`)
	dashPattern        = regexp.MustCompile(`-+`)
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

func SanitizePath(path string) string {
	path = strings.ToLower(path)
	path = invalidRunePattern.ReplaceAllString(path, "")
	path = whitespacePattern.ReplaceAllString(path, "-")
	path = dashPattern.ReplaceAllString(path, "-")
	return path
}
