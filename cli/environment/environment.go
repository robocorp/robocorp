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
	digest := calculateDigest(cfg.GetPath(), *condaYaml)

	if env, ok := cache.GetEntry(digest); ok {
		return mergeEnvironment(env), true
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

	digest := calculateDigest(cfg.GetPath(), *condaYaml)
	space := fmt.Sprintf("robo-%v", digest)

	env, err := rcc.HolotreeVariables(condaPath, space, onProgress)
	if err != nil {
		return Environment{}, err
	}

	if err := cache.AddEntry(digest, env); err != nil {
		return Environment{}, err
	}

	return mergeEnvironment(env), nil
}

func mergeEnvironment(holotree map[string]string) Environment {
	// Propagate user environment
	env := getEnvironment()

	// Ignore Python-specific overrides
	delete(env, "PYTHONPATH")
	delete(env, "PYTHONHOME")
	delete(env, "PYTHONSTARTUP")
	delete(env, "PYTHONEXECUTABLE")

	// Merge with rcc environment
	for k, v := range holotree {
		env[k] = v
	}

	return Environment{Variables: env}
}

func calculateDigest(projectPath string, condaYaml conda.CondaYaml) string {
	condaContent, err := json.Marshal(condaYaml)
	if err != nil {
		panic(err)
	}

	hash := md5.New()
	hash.Write([]byte(projectPath))
	hash.Write(condaContent)

	digest := hex.EncodeToString(hash.Sum(nil))
	return digest[:16]
}
