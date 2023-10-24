package process

import (
	"bufio"
	"fmt"
	"io"
	"os/exec"
	"strings"
	"sync"
)

var (
	procs []*Process
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

func KillAll() []error {
	errors := make([]error, 0)
	for _, proc := range procs {
		if err := proc.cmd.Process.Kill(); err != nil {
			errors = append(errors, err)
		}
	}
	return errors
}

func New(name string, args ...string) *Process {
	return &Process{name: name, args: args}
}

func (proc *Process) String() string {
	return fmt.Sprintf("Process[name='%v',args=%v]", proc.name, proc.args)
}

func (proc *Process) Run() (*Output, *ProcessError) {
	proc.cmd = exec.Command(proc.name, proc.args...)

	if proc.Env != nil {
		proc.cmd.Env = proc.Env
	}

	var stdout, stderr []string
	var wg sync.WaitGroup

	stdoutPipe, err := proc.cmd.StdoutPipe()
	if err != nil {
		return nil, &ProcessError{Err: err}
	}

	stderrPipe, err := proc.cmd.StderrPipe()
	if err != nil {
		return nil, &ProcessError{Err: err}
	}

	wg.Add(1)
	go func() {
		var line string
		var err error
		reader := bufio.NewReader(stdoutPipe)
		for err == nil {
			line, err = reader.ReadString('\n')
			if proc.StdoutListener != nil {
				proc.StdoutListener(line)
			}
			stdout = append(stdout, line)
		}
		wg.Done()
		if err != io.EOF {
			panic(err)
		}
	}()

	wg.Add(1)
	go func() {
		var line string
		var err error
		reader := bufio.NewReader(stderrPipe)
		for err == nil {
			line, err = reader.ReadString('\n')
			if proc.StderrListener != nil {
				proc.StderrListener(line)
			}
			stderr = append(stderr, line)
		}
		wg.Done()
		if err != io.EOF {
			panic(err)
		}
	}()

	procs = append(procs, proc)
	if err := proc.cmd.Start(); err != nil {
		return nil, &ProcessError{Err: err}
	}

	wg.Wait()
	err = proc.cmd.Wait()

	output := &Output{
		Stdout: strings.Join(stdout, ""),
		Stderr: strings.Join(stderr, ""),
	}

	if err != nil {
		return nil, &ProcessError{Err: err, Output: output}
	} else {
		return output, nil
	}
}
