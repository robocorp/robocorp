package process

import (
	"bufio"
	"errors"
	"fmt"
	"os/exec"
	"strings"
	"sync"
)

type Process struct {
	name           string
	args           []string
	cmd            *exec.Cmd
	StdoutListener func(string)
	StderrListener func(string)
	Env            []string
}

type Output struct {
	Stdout string
	Stderr string
}

func (o Output) AsError() error {
	return errors.New(o.Stderr)
}

func New(name string, args ...string) *Process {
	return &Process{name: name, args: args}
}

func (proc *Process) String() string {
	return fmt.Sprintf("Process[name='%v',args=%v]", proc.name, proc.args)
}

func (proc *Process) Run() (*Output, error) {
	proc.cmd = exec.Command(proc.name, proc.args...)

	if proc.Env != nil {
		proc.cmd.Env = proc.Env
	}

	var stdout, stderr []string
	var wg sync.WaitGroup

	stdoutPipe, err := proc.cmd.StdoutPipe()
	if err != nil {
		panic(err)
	}

	stderrPipe, err := proc.cmd.StderrPipe()
	if err != nil {
		panic(err)
	}

	wg.Add(1)
	go func() {
		scanner := bufio.NewScanner(stdoutPipe)
		for scanner.Scan() {
			line := scanner.Text()
			if proc.StdoutListener != nil {
				proc.StdoutListener(line)
			}
			stdout = append(stdout, line)
		}
		wg.Done()
	}()

	wg.Add(1)
	go func() {
		scanner := bufio.NewScanner(stderrPipe)
		for scanner.Scan() {
			line := scanner.Text()
			if proc.StderrListener != nil {
				proc.StderrListener(line)
			}
			stderr = append(stderr, line)
		}
		wg.Done()
	}()

	err = proc.cmd.Run()
	wg.Wait()

	output := &Output{
		Stdout: strings.Join(stdout, "\n"),
		Stderr: strings.Join(stderr, "\n"),
	}

	return output, err
}
