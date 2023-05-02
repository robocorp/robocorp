package environment

import (
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"

	"github.com/robocorp/robo/cli/config/conda"
	"github.com/robocorp/robo/cli/config/pyproject"
	"github.com/robocorp/robo/cli/environment/cache"
	"github.com/robocorp/robo/cli/paths"
	"github.com/robocorp/robo/cli/rcc"
)

type Environment struct {
	Variables map[string]string
}

func (e Environment) ToSlice() []string {
	env := make([]string, 0)
	for k, v := range e.Variables {
		env = append(env, fmt.Sprintf("%v=%v", k, v))
	}
	return env
}

func TryCache(cfg pyproject.Robo) (Environment, bool) {
	condaYaml := conda.NewFromConfig(cfg)
	digest := digest(cfg.GetPath(), *condaYaml)

	if env, ok := cache.Get(digest); ok {
		return Environment{merge(env)}, true
	} else {
		return Environment{}, false
	}
}

func Create(
	cfg pyproject.Robo,
	onProgress func(*rcc.Progress),
) (Environment, error) {
	condaPath := paths.CreateTempFile(cfg.GetPath(), ".conda-*.yaml")
	defer os.Remove(condaPath)

	condaYaml := conda.NewFromConfig(cfg)
	if err := condaYaml.SaveAs(condaPath); err != nil {
		return Environment{}, err
	}

	key := digest(cfg.GetPath(), *condaYaml)
	space := fmt.Sprintf("robo-%v", key)

	env, err := rcc.HolotreeVariables(condaPath, space, onProgress)
	if err != nil {
		return Environment{}, err
	}

	if err := cache.Add(key, env); err != nil {
		return Environment{}, err
	}

	return Environment{merge(env)}, nil
}

func merge(holotree map[string]string) map[string]string {
	env := environ()

	delete(env, "PYTHONPATH")
	delete(env, "PYTHONHOME")
	delete(env, "PYTHONSTARTUP")
	delete(env, "PYTHONEXECUTABLE")

	for k, v := range holotree {
		env[k] = v
	}

	return env
}

func digest(projectPath string, condaYaml conda.CondaYaml) string {
	condaContent, err := json.Marshal(condaYaml)
	if err != nil {
		panic(err)
	}

	hash := md5.New()
	hash.Write([]byte(projectPath))
	hash.Write(condaContent)

	checksum := hex.EncodeToString(hash.Sum(nil))
	return checksum[:16]
}
