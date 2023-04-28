package rcc

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
)

var (
	progressPattern = regexp.MustCompile(
		`^#{4}\s+Progress:\s+` +
			`(?P<current>\d+)\/(?P<total>\d+)\s+` +
			`(?P<version>\S+)\s+` +
			`(?P<duration>\S+)\s+` +
			`(?P<message>.+)`,
	)
)

type Progress struct {
	Current  int
	Total    int
	Version  string
	Duration string
	Message  string
}

func (p Progress) String() string {
	return fmt.Sprintf("Progress[%v/%v]: %v", p.Current, p.Total, p.Message)
}

func ParseProgress(line string) *Progress {
	line = strings.TrimSpace(line)
	matches := progressPattern.FindStringSubmatch(line)
	if len(matches) != 6 {
		return nil
	}

	current, err := strconv.Atoi(matches[1])
	if err != nil {
		return nil
	}

	total, err := strconv.Atoi(matches[2])
	if err != nil {
		return nil
	}

	return &Progress{
		Current:  current,
		Total:    total,
		Version:  matches[3],
		Duration: matches[4],
		Message:  matches[5],
	}
}
