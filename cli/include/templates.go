package include

import (
	"fmt"
	"path"

	"github.com/robocorp/robo/cli/paths"
	yaml "gopkg.in/yaml.v3"
)

type TemplatesYaml struct {
	Templates []Template `yaml:"templates"`
}

type Template struct {
	Name        string `yaml:"name"`
	Description string `yaml:"desc"`
	DirName     string `yaml:"dirName"`
}

func Templates() []Template {
	data, err := inc.ReadFile("templates/templates.yaml")
	if err != nil {
		panic(err)
	}

	var templates TemplatesYaml
	if err := yaml.Unmarshal(data, &templates); err != nil {
		panic(err)
	}

	return templates.Templates
}

func (t Template) FilterValue() string { return t.Name }

func (t *Template) Copy(dst string) error {
	src := path.Join("templates", t.DirName)
	exists, err := paths.Exists(dst)
	if exists {
		return fmt.Errorf("Path already exists: %v", dst)
	}
	if err != nil {
		return err
	}

	return CopyDir(src, dst, 0o755)
}
