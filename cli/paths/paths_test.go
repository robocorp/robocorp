package paths

import (
    "testing"
    "github.com/google/go-cmp/cmp"
)

func TestSanitize(t *testing.T) {
    tests := map[string]struct {
        input string
        want  string
    }{
        "simple": {input: "Simple", want: "simple"},
        "spaces": {input: "Spaces In  A name", want: "spaces-in-a-name"},
        "underscores": {input: "some_underscores_in_here", want: "some-underscores-in-here"},
        "empty": {input: "", want: ""},
        "mixed": {input: "a very-_complicated_ _ -set of     strings", want: "a-very-complicated-set-of-strings"},
        "invalid": {input: "€o()=o)p%€s#", want: "oops"},
    }

    for name, tc := range tests {
        t.Run(name, func(t *testing.T) {
            got := Sanitize(tc.input)
            diff := cmp.Diff(tc.want, got)
            if diff != "" {
                t.Fatalf(diff)
            }
        })
    }
}
