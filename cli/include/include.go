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
	if err := os.MkdirAll(parent, mode); err != nil {
		return err
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

	if err := os.MkdirAll(dst, mode); err != nil {
		return err
	}

	for _, entry := range entries {
		entrySrc := path.Join(src, entry.Name())

		if entry.IsDir() {
			dir := path.Join(dst, entry.Name())
			if err := CopyDir(entrySrc, dir, mode); err != nil {
				return err
			}
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
