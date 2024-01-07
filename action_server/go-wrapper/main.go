package main

import (
	"embed"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
)

//go:embed all:assets/*
var content embed.FS

func copyFiles(src, dest string) error {
	files, err := content.ReadDir(src)
	if err != nil {
		return err
	}

	for _, file := range files {
		// srcPath can't be constructed with filepath.Join because embed needs `/` as sep even on Windows
		srcPath := fmt.Sprintf("%s/%s", src, file.Name())
		destPath := filepath.Join(dest, file.Name())

		if file.IsDir() {
			err := copyFiles(srcPath, destPath)
			if err != nil {
				return err
			}
		} else {
			fileContent, err := content.ReadFile(srcPath)
			if err != nil {
				return err
			}

			err = os.MkdirAll(filepath.Dir(destPath), 0755)
			if err != nil {
				return err
			}

			err = os.WriteFile(destPath, fileContent, 0755)
			if err != nil {
				return err
			}
		}
	}

	return nil
}

func main() {
	var actionServerPath string
	var executablePath string

	// Read the version
	versionData, err := content.ReadFile("assets/version.txt")
	if err != nil {
		fmt.Println("Error reading version.txt:", err)
		os.Exit(1)
	}
	version := strings.TrimSpace(string(versionData))

	// Determine the appropriate path based on the operating system
	switch runtime.GOOS {
	case "windows":
		appDataDir := os.Getenv("LOCALAPPDATA")
		actionServerPath = fmt.Sprintf("%s\\robocorp\\action-server\\%s", appDataDir, version)
		executablePath = filepath.Join(actionServerPath, "action-server.exe")
	case "linux", "darwin":
		homeDir, err := os.UserHomeDir()
		if err != nil {
			fmt.Println("Error getting user home directory:", err)
			os.Exit(1)
		}
		actionServerPath = fmt.Sprintf("%s/.robocorp/action-server/%s", homeDir, version)
		executablePath = filepath.Join(actionServerPath, "action-server")
	default:
		fmt.Println("Unsupported operating system")
		os.Exit(1)
	}

	// If the folder doesn't exist already, we create it and copy all files
	_, err = os.Stat(actionServerPath)
	if os.IsNotExist(err) {
		err = os.MkdirAll(actionServerPath, 0755)
		if err != nil {
			fmt.Println("Error creating directory:", err)
			os.Exit(1)
		}

		err = copyFiles("assets", actionServerPath)
		if err != nil {
			fmt.Println("Error copying files:", err)
			os.Exit(1)
		}
	}

	cmd := exec.Command(executablePath, os.Args[1:]...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Stdin = os.Stdin

	err = cmd.Run()
	if err != nil {
		fmt.Println("Error executing action-server:", err)
		os.Exit(1)
	}
}
