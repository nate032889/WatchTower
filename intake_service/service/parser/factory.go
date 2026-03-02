package parser

import (
	"path/filepath"
)

// GetParser returns the appropriate Parser implementation based on the file extension.
func GetParser(filename string) Parser {
	ext := filepath.Ext(filename)
	switch ext {
	case ".txt", ".md", ".json":
		return &TextParser{}
	case ".pcap":
		return &PcapParser{}
	case ".pcapng":
		return &PcapParser{}
	case ".pdf":
		return &PdfParser{}
	case ".docx", ".pptx":
		return &OfficeParser{}
	default:
		return &BinaryParser{}
	}
}
