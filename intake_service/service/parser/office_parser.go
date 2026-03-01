package parser

import (
	"archive/zip"
	"bytes"
	"encoding/xml"
	"fmt"
	"io"
	"strings"
)

// OfficeParser handles .docx and .pptx files.
type OfficeParser struct{}

func (p *OfficeParser) Parse(data []byte) (string, error) {
	reader, err := zip.NewReader(bytes.NewReader(data), int64(len(data)))
	if err != nil {
		return "", fmt.Errorf("failed to open office file as zip: %w", err)
	}

	var sb strings.Builder

	for _, file := range reader.File {
		// For Word documents, the main content is in word/document.xml
		if file.Name == "word/document.xml" {
			content, err := extractTextFromXML(file)
			if err != nil {
				return "", fmt.Errorf("failed to extract text from docx: %w", err)
			}
			sb.WriteString(content)
		}

		// For PowerPoint, content is spread across ppt/slides/slide*.xml
		if strings.HasPrefix(file.Name, "ppt/slides/slide") && strings.HasSuffix(file.Name, ".xml") {
			content, err := extractTextFromXML(file)
			if err != nil {
				continue // Skip problematic slides but try to continue
			}
			sb.WriteString(fmt.Sprintf("\n--- Slide: %s ---\n", file.Name))
			sb.WriteString(content)
		}
	}

	if sb.Len() == 0 {
		return "", fmt.Errorf("no extractable text found in office document")
	}

	return sb.String(), nil
}

// extractTextFromXML reads an XML file from the zip and extracts all text content.
func extractTextFromXML(file *zip.File) (string, error) {
	rc, err := file.Open()
	if err != nil {
		return "", err
	}
	defer rc.Close()

	decoder := xml.NewDecoder(rc)
	var sb strings.Builder

	for {
		token, err := decoder.Token()
		if err == io.EOF {
			break
		}
		if err != nil {
			return "", err
		}

		switch t := token.(type) {
		case xml.CharData:
			text := string(t)
			if strings.TrimSpace(text) != "" {
				sb.WriteString(text)
				sb.WriteString(" ")
			}
		}
	}

	return sb.String(), nil
}
