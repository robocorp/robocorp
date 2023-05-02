package cache

import (
	"encoding/json"
	"os"
	"path"

	"github.com/robocorp/robo/cli/paths"
)

type Cache map[string]map[string]string

var (
	filename string
)

func init() {
	filename = path.Join(paths.RoboHome(), ".envcache.json")
}

func Get(key string) (map[string]string, bool) {
	cache := load()
	values, ok := cache[key]
	return values, ok
}

func Add(key string, values map[string]string) error {
	cache := load()
	cache[key] = values

	data, err := json.Marshal(cache)
	if err != nil {
		return err
	}

	return os.WriteFile(filename, data, 0o644)
}

func load() Cache {
	data, err := os.ReadFile(filename)
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
