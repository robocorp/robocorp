package main

import (
	"embed"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"

	"golang.org/x/mod/semver"
)

//go:embed all:assets/*
var content embed.FS

// Constants
const ACTION_SERVER_LATEST_BASE_URL = "https://downloads.robocorp.com/action-server/releases/latest/"
const VERSION_LATEST_URL = ACTION_SERVER_LATEST_BASE_URL + "version.txt"

type ColorType struct{}

func (ct *ColorType) Bold(str string) string {
	return fmt.Sprintf("\033[1m%s\033[0m", str)
}
func (ct *ColorType) Yellow(str string) string {
	return fmt.Sprintf("\033[33m%s\033[0m", str)
}
func (ct *ColorType) Green(str string) string {
	return fmt.Sprintf("\033[32m%s\033[0m", str)
}

func getLatestVersion() (string, error) {
	// Get the data from the URL
	versionResponse, err := http.Get(VERSION_LATEST_URL)
	if err != nil {
		return "", err
	}
	defer versionResponse.Body.Close()

	// Read the body content
	versionInBytes, err := io.ReadAll(versionResponse.Body)
	if err != nil {
		return "", err
	}
	// Convert the byte slice to string
	versionAsString := string(versionInBytes)
	return strings.TrimSpace(versionAsString), nil
}

func checkAvailableUpdate(version string) {
	// Get the latest version
	latestVersion, err := getLatestVersion()
	if err != nil {
		fmt.Println("Verifying latest version failed:", err)
		return
	}
	// Compare the given version with the latest one
	compareResult := semver.Compare(strings.TrimSpace("v"+version), strings.TrimSpace("v"+latestVersion))

	// If the current version is a previous version than the latest print the update suggestions
	if compareResult == -1 {
		// Construct the needed URL path to get to the downloadable object
		var actionOS, actionExe string
		switch runtime.GOOS {
		case "windows":
			actionOS = "windows64"
			actionExe = "action-server.exe"
		case "linux":
			actionOS = "linux64"
			actionExe = "action-server"
		case "darwin":
			actionOS = "macos64"
			actionExe = "action-server"
		default:
			fmt.Println("Unsupported operating system")
			os.Exit(1)
		}
		colorT := &ColorType{}
		urlPath, _ := url.JoinPath(ACTION_SERVER_LATEST_BASE_URL, actionOS, actionExe)
		fmt.Printf("\n ⏫ A new version of action-server is now available: %s → %s \n", colorT.Yellow(version), colorT.Green(latestVersion))
		if runtime.GOOS == "darwin" {
			fmt.Printf("    To update, download from: %s \n", colorT.Bold(urlPath))
			fmt.Printf("    Or run: %s \n\n", colorT.Bold("brew update && brew install robocorp/tools/action-server"))
		} else {
			fmt.Printf("    To update, download from: %s \n\n", colorT.Bold(urlPath))
		}
	}
}

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

	// Check if there is an update available
	checkAvailableUpdate(version)

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
