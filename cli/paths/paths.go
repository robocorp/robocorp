package paths

import (
	"os"
	"path"
	"path/filepath"
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

func Exists(path string) (bool, error) {
	if _, err := os.Stat(path); err != nil {
		if os.IsNotExist(err) {
			return false, nil
		} else {
			return false, err
		}
	}

	return true, nil
}

func Sanitize(path string) string {
	path = strings.ToLower(path)
	path = invalidRunePattern.ReplaceAllString(path, "")
	path = whitespacePattern.ReplaceAllString(path, "-")
	path = dashPattern.ReplaceAllString(path, "-")
	return path
}

func IsChild(parent, child string) (bool, error) {
	// NB: Comparing Abs() paths is not entirely reliable with symlinks,
	//     but is alright enough for our use-case
	parentAbs, err := filepath.Abs(parent)
	if err != nil {
		return false, err
	}
	childAbs, err := filepath.Abs(child)
	if err != nil {
		return false, err
	}

	rel, err := filepath.Rel(parentAbs, childAbs)
	if err != nil {
		return false, err
	}

	if rel == "." {
		return false, nil
	}

	prefix := ".." + string(os.PathSeparator)
	if strings.HasPrefix(rel, prefix) {
		return false, nil
	}

	return true, nil
}
