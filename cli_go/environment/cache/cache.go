package cache

import (
	"encoding/json"
	"os"
	"path"

	"github.com/robocorp/robo/cli/paths"
)

type Cache map[string]map[string]string

var (
	cachePath string
)

func init() {
	cachePath = path.Join(paths.RoboHome(), ".envcache.json")
}

func GetEntry(key string) (map[string]string, bool) {
	cache := loadCache()
	values, ok := cache[key]
	return values, ok
}

func AddEntry(key string, values map[string]string) error {
	cache := loadCache()
	cache[key] = values

	data, err := json.Marshal(cache)
	if err != nil {
		return err
	}

	return os.WriteFile(cachePath, data, 0o644)
}

func loadCache() Cache {
	data, err := os.ReadFile(cachePath)
	if err != nil {
		return make(Cache)
	}

	var cache Cache
	err = json.Unmarshal(data, &cache)
	if err != nil {
		return make(Cache)
	}

	return cache
}
