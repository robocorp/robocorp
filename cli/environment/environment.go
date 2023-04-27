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

func EnsureFromConfig(
	cfg pyproject.Robo,
	onProgress func(*rcc.Progress),
) (Environment, error) {
	// TODO: Get root from somewhere else
	projectRoot, err := os.Getwd()
	if err != nil {
		return Environment{}, err
	}

	condaYaml := conda.NewFromConfig(cfg)

	digest := calculateDigest(projectRoot, *condaYaml)
	if cachedEnv, ok := cache.GetEntry(digest); ok {
		return mergeEnvironment(cachedEnv), nil
	}

	env, err := createEnvironment(projectRoot, condaYaml, onProgress)
	if err != nil {
		return Environment{}, err
	}

	return mergeEnvironment(env), nil
}

func createEnvironment(
	projectRoot string,
	condaYaml *conda.CondaYaml,
	onProgress func(*rcc.Progress),
) (map[string]string, error) {
	condaPath := paths.CreateTempFile(projectRoot, ".conda-*.yaml")
	defer os.Remove(condaPath)

	err := condaYaml.SaveAs(condaPath)
	if err != nil {
		return nil, err
	}

	digest := calculateDigest(projectRoot, *condaYaml)
	space := fmt.Sprintf("robo-%v", digest)

	vars, err := rcc.HolotreeVariables(condaPath, space, onProgress)
	if err != nil {
		return nil, err
	}

	err = cache.AddEntry(digest, vars)
	if err != nil {
		return nil, err
	}

	return vars, nil
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
