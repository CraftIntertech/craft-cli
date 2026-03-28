package cmd

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"runtime"
	"strings"

	"github.com/fatih/color"
)

const releaseAPI = "https://api.github.com/repos/CraftIntertech/craft-cli/releases/latest"

type githubRelease struct {
	TagName string        `json:"tag_name"`
	Name    string        `json:"name"`
	Assets  []githubAsset `json:"assets"`
	HTMLURL string        `json:"html_url"`
}

type githubAsset struct {
	Name               string `json:"name"`
	BrowserDownloadURL string `json:"browser_download_url"`
	Size               int64  `json:"size"`
}

func binaryName() string {
	goos := runtime.GOOS
	goarch := runtime.GOARCH
	name := fmt.Sprintf("craft-%s-%s", goos, goarch)
	if goos == "windows" {
		name += ".exe"
	}
	return name
}

func runUpdate() {
	fmt.Printf("Current version: %s\n", Version)
	fmt.Println("Checking for updates...")

	// Fetch latest release info
	resp, err := http.Get(releaseAPI)
	if err != nil {
		color.Red("Error: Could not check for updates — %v", err)
		os.Exit(1)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		color.Red("Error: Could not check for updates (HTTP %d)", resp.StatusCode)
		fmt.Println("Download manually: https://github.com/CraftIntertech/craft-cli/releases")
		os.Exit(1)
	}

	var release githubRelease
	if err := json.NewDecoder(resp.Body).Decode(&release); err != nil {
		color.Red("Error: Could not parse release info — %v", err)
		os.Exit(1)
	}

	latestVersion := strings.TrimPrefix(release.TagName, "v")
	currentVersion := strings.TrimPrefix(Version, "v")

	if latestVersion == currentVersion {
		color.Green("Already up to date (v%s).", currentVersion)
		return
	}

	fmt.Printf("New version available: %s → %s\n", currentVersion, latestVersion)

	// Find matching binary asset
	target := binaryName()
	var downloadURL string
	var assetSize int64
	for _, asset := range release.Assets {
		if asset.Name == target {
			downloadURL = asset.BrowserDownloadURL
			assetSize = asset.Size
			break
		}
	}

	if downloadURL == "" {
		color.Yellow("No binary found for %s/%s.", runtime.GOOS, runtime.GOARCH)
		fmt.Printf("Download manually: %s\n", release.HTMLURL)
		return
	}

	fmt.Printf("Downloading %s (%.1f MB)...\n", target, float64(assetSize)/(1024*1024))

	// Download the binary
	dlResp, err := http.Get(downloadURL)
	if err != nil {
		color.Red("Error: Download failed — %v", err)
		os.Exit(1)
	}
	defer dlResp.Body.Close()

	if dlResp.StatusCode != 200 {
		color.Red("Error: Download failed (HTTP %d)", dlResp.StatusCode)
		os.Exit(1)
	}

	// Get current executable path
	execPath, err := os.Executable()
	if err != nil {
		color.Red("Error: Could not determine executable path — %v", err)
		os.Exit(1)
	}

	// Write to temp file next to executable
	tmpPath := execPath + ".tmp"
	tmpFile, err := os.OpenFile(tmpPath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0755)
	if err != nil {
		color.Red("Error: Could not write update — %v", err)
		fmt.Println("Try running with sudo or check file permissions.")
		os.Exit(1)
	}

	_, err = io.Copy(tmpFile, dlResp.Body)
	tmpFile.Close()
	if err != nil {
		os.Remove(tmpPath)
		color.Red("Error: Download incomplete — %v", err)
		os.Exit(1)
	}

	// Replace current binary
	if err := os.Rename(tmpPath, execPath); err != nil {
		os.Remove(tmpPath)
		color.Red("Error: Could not replace binary — %v", err)
		fmt.Println("Try running with sudo.")
		os.Exit(1)
	}

	color.Green("Updated: v%s → v%s", currentVersion, latestVersion)
}
