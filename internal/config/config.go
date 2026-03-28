package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// Config holds the CLI configuration.
type Config struct {
	BaseURL      string `json:"base_url"`
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
}

const defaultBaseURL = "https://craftintertech.co.th/api/v1"

// configDir returns the path to the config directory (~/.config/craft).
func configDir() string {
	home, err := os.UserHomeDir()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: cannot determine home directory: %v\n", err)
		os.Exit(1)
	}
	return filepath.Join(home, ".config", "craft")
}

// configPath returns the full path to the config file.
func configPath() string {
	return filepath.Join(configDir(), "config.json")
}

// LoadConfig reads the config file and returns the Config struct.
// If the file does not exist, a default Config is returned.
func LoadConfig() Config {
	cfg := Config{
		BaseURL: defaultBaseURL,
	}

	data, err := os.ReadFile(configPath())
	if err != nil {
		// File doesn't exist or can't be read; return defaults.
		return cfg
	}

	if err := json.Unmarshal(data, &cfg); err != nil {
		// Malformed config; return defaults.
		return Config{BaseURL: defaultBaseURL}
	}

	if cfg.BaseURL == "" {
		cfg.BaseURL = defaultBaseURL
	}

	return cfg
}

// SaveConfig writes the Config struct to the config file with 0600 permissions.
func SaveConfig(cfg Config) {
	dir := configDir()
	if err := os.MkdirAll(dir, 0700); err != nil {
		fmt.Fprintf(os.Stderr, "Error: cannot create config directory: %v\n", err)
		os.Exit(1)
	}

	data, err := json.MarshalIndent(cfg, "", "  ")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: cannot marshal config: %v\n", err)
		os.Exit(1)
	}

	if err := os.WriteFile(configPath(), data, 0600); err != nil {
		fmt.Fprintf(os.Stderr, "Error: cannot write config file: %v\n", err)
		os.Exit(1)
	}
}

// GetToken returns the current access token.
func GetToken() string {
	cfg := LoadConfig()
	return cfg.AccessToken
}

// SaveTokens stores both access and refresh tokens in the config.
func SaveTokens(access, refresh string) {
	cfg := LoadConfig()
	cfg.AccessToken = access
	cfg.RefreshToken = refresh
	SaveConfig(cfg)
}

// ClearTokens removes both tokens from the config.
func ClearTokens() {
	cfg := LoadConfig()
	cfg.AccessToken = ""
	cfg.RefreshToken = ""
	SaveConfig(cfg)
}

// GetBaseURL returns the configured base URL.
func GetBaseURL() string {
	cfg := LoadConfig()
	return cfg.BaseURL
}
