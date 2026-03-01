package parser

// Parser defines the interface for processing different file types.
type Parser interface {
	Parse(data []byte) (string, error)
}
