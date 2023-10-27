package cache

import (
	"encoding/json"
	"os"
	"path"

	"github.com/robocorp/robo/cli/paths"
)

type CacheEntry struct {
	Variables    map[string]string `json:"variables"`
	Capabilities struct {
		Tasks  bool `json:"tasks"`
		Server bool `json:"server"`
	} `json:"capabilities"`
}

type CacheFile map[string]CacheEntry

var (
	cacheFile string
)

func init() {
	cacheFile = path.Join(paths.RoboHome(), ".envcache.json")
}

func Get(key string) (CacheEntry, bool) {
	cache := load()
	values, ok := cache[key]
	return values, ok
}

func Add(key string, entry CacheEntry) error {
	cache := load()
	cache[key] = entry

	data, err := json.Marshal(cache)
	if err != nil {
		return err
	}

	return os.WriteFile(cacheFile, data, 0o644)
}

func load() CacheFile {
	data, err := os.ReadFile(cacheFile)
	if err != nil {
		return make(CacheFile)
	}

	var cache CacheFile
	err = json.Unmarshal(data, &cache)
	if err != nil {
		return make(CacheFile)
	}

	return cache
}
