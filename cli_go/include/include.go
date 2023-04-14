package include

import (
	"embed"
	"io/fs"
	"os"
	"path"
)

//go:embed bin/*
//go:embed all:templates/*
var inc embed.FS

func CopyFile(src, dst string, mode fs.FileMode) error {
	data, err := inc.ReadFile(src)
	if err != nil {
		return err
	}

	parent := path.Dir(dst)
	if _, err := os.Stat(parent); os.IsNotExist(err) {
		os.MkdirAll(parent, mode)
	}

	if err := os.WriteFile(dst, data, mode); err != nil {
		return err
	}

	return nil
}

func CopyDir(src, dst string, mode fs.FileMode) error {
	entries, err := inc.ReadDir(src)
	if err != nil {
		return err
	}

	if _, err := os.Stat(dst); os.IsNotExist(err) {
		os.MkdirAll(dst, mode)
	}

	for _, entry := range entries {
		entrySrc := path.Join(src, entry.Name())

		if entry.IsDir() {
			CopyDir(entrySrc, path.Join(dst, entry.Name()), mode)
			continue
		}

		data, err := inc.ReadFile(entrySrc)
		if err != nil {
			return err
		}

		entryDst := path.Join(dst, entry.Name())
		if err := os.WriteFile(entryDst, data, mode); err != nil {
			return err
		}
	}

	return nil
}
