package process

import (
	"bufio"
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

type ProcessError struct {
	Err    error
	Output *Output
}

func (p ProcessError) Error() string {
	if p.Output != nil {
		return p.Output.Stderr
	} else {
		return p.Err.Error()
	}
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

	if err != nil {
		return nil, ProcessError{Err: err, Output: output}
	} else {
		return output, nil
	}
}
