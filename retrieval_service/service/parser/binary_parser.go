package parser

import (
	"bytes"
	"crypto/sha256"
	"debug/elf"
	"debug/pe"
	"encoding/hex"
	"fmt"
	"strings"
	"unicode"
)

// BinaryParser handles executable and unknown binary files.
type BinaryParser struct{}

// Parse performs static analysis on the binary data.
func (p *BinaryParser) Parse(data []byte) (string, error) {
	var sb strings.Builder

	// 1. Basic Metadata & Hash
	// Useful for the LLM to identify the file or for the user to cross-reference (e.g. VirusTotal).
	hash := sha256.Sum256(data)
	sb.WriteString("Binary Analysis Report\n")
	sb.WriteString("----------------------\n")
	sb.WriteString(fmt.Sprintf("Size: %d bytes\n", len(data)))
	sb.WriteString(fmt.Sprintf("SHA256: %s\n", hex.EncodeToString(hash[:])))
	sb.WriteString("\n")

	// 2. Format Analysis (PE vs ELF)
	// We attempt to parse headers to find imported libraries (capabilities).
	reader := bytes.NewReader(data)

	// Try parsing as Windows PE
	if peFile, err := pe.NewFile(reader); err == nil {
		sb.WriteString("Format: Windows PE Executable\n")

		// Imported Libraries (DLLs) tell us high-level capabilities (Networking, GUI, etc.)
		if libs, err := peFile.ImportedLibraries(); err == nil {
			sb.WriteString("\n[Imported Libraries]\n")
			for _, lib := range libs {
				sb.WriteString(fmt.Sprintf("- %s\n", lib))
			}
		}

		// Imported Symbols (Functions) give granular detail (e.g., "InternetOpenA")
		if symbols, err := peFile.ImportedSymbols(); err == nil {
			sb.WriteString("\n[Imported Functions (First 20)]\n")
			count := 0
			for _, sym := range symbols {
				if count >= 20 {
					sb.WriteString("... (truncated)\n")
					break
				}
				sb.WriteString(fmt.Sprintf("- %s\n", sym))
				count++
			}
		}
	} else {
		// Reset reader and try parsing as Linux ELF
		reader.Seek(0, 0)
		if elfFile, err := elf.NewFile(reader); err == nil {
			sb.WriteString("Format: Linux ELF Executable\n")
			sb.WriteString(fmt.Sprintf("Machine Architecture: %s\n", elfFile.Machine.String()))

			if libs, err := elfFile.ImportedLibraries(); err == nil {
				sb.WriteString("\n[Imported Libraries]\n")
				for _, lib := range libs {
					sb.WriteString(fmt.Sprintf("- %s\n", lib))
				}
			}

			if symbols, err := elfFile.ImportedSymbols(); err == nil {
				sb.WriteString("\n[Imported Functions (First 20)]\n")
				count := 0
				for _, sym := range symbols {
					if count >= 20 {
						sb.WriteString("... (truncated)\n")
						break
					}
					sb.WriteString(fmt.Sprintf("- %s\n", sym.Name))
					count++
				}
			}
		} else {
			sb.WriteString("Format: Unknown / Raw Binary\n")
		}
	}

	// 3. Strings Extraction
	// Extracts printable strings to find URLs, IPs, paths, etc.
	sb.WriteString("\n[Extracted Strings (First 50 > 4 chars)]\n")
	extracted := extractStrings(data, 4, 50)
	for _, s := range extracted {
		sb.WriteString(fmt.Sprintf("%s\n", s))
	}

	return sb.String(), nil
}

// extractStrings finds sequences of printable characters.
// minLength: Minimum length of string to be considered valid.
// maxCount: Maximum number of strings to return to save context window.
func extractStrings(data []byte, minLength int, maxCount int) []string {
	var found []string
	var current []rune

	for _, b := range data {
		r := rune(b)
		if unicode.IsPrint(r) {
			current = append(current, r)
		} else {
			if len(current) >= minLength {
				found = append(found, string(current))
				if len(found) >= maxCount {
					return found
				}
			}
			current = nil
		}
	}
	// Check if the file ended with a string
	if len(current) >= minLength && len(found) < maxCount {
		found = append(found, string(current))
	}
	return found
}
