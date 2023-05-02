package rcc

import (
	"encoding/json"
	"fmt"

	"github.com/robocorp/robo/cli/paths"
	"github.com/robocorp/robo/cli/process"
)

type variables []struct {
	Key   string `json:"key"`
	Value string `json:"value"`
}

// rcc holotree variables
func HolotreeVariables(
	condaConfig string,
	space string,
	onProgress func(*Progress),
) (map[string]string, error) {
	Ensure()

	proc := process.New(
		paths.RccBin,
		"holotree",
		"variables",
		"--json",
		"--colorless",
		"--space",
		space,
		"--controller",
		Controller,
		condaConfig,
	)

	if onProgress != nil {
		proc.StderrListener = func(line string) {
			if progress := ParseProgress(line); progress != nil {
				onProgress(progress)
			}
		}
	}

	output, err := proc.Run()
	if err != nil {
		return nil, fmt.Errorf("Failed to create environment: %v", err)
	}

	var vars variables
	if err := json.Unmarshal([]byte(output.Stdout), &vars); err != nil {
		return nil, err
	}

	result := make(map[string]string, 0)
	for _, val := range vars {
		result[val.Key] = val.Value
	}

	return result, nil
}

// rcc robot wrap
func RobotWrap(path string) error {
	Ensure()

	proc := process.New(
		paths.RccBin,
		"robot",
		"wrap",
		"--zipfile",
		path,
	)

	if _, err := proc.Run(); err != nil {
		return fmt.Errorf("Failed to package project: %v", err)
	}

	return nil
}
