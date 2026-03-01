package parser

// TextParser handles plain text, markdown, and JSON files.
type TextParser struct{}

func (p *TextParser) Parse(data []byte) (string, error) {
	return string(data), nil
}
