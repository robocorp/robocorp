package export

import (
	"fmt"
	"os"

	"github.com/robocorp/robo/cli/operations/lock"
	"github.com/robocorp/robo/cli/rcc"
	"github.com/robocorp/robo/cli/ui"
)

const (
	CondaPath = "conda.yaml"
	RobotPath = "robot.yaml"
)

var (
	bold  = ui.DefaultStyles().Bold
	title = bold.Margin(1, 0)
)

func ExportProject(dir, zipFile string, force bool) error {
	files, err := lock.CreateLockFiles(dir, force)
	if err != nil {
		return err
	}

	for _, f := range files {
		defer os.Remove(f)
	}

	if err := rcc.RobotWrap(zipFile); err != nil {
		return fmt.Errorf("Failed to create zip file: %v", err)
	}

	fmt.Println(bold.Inline(true).Render("Created zipfile:"), zipFile)

	return nil
}
