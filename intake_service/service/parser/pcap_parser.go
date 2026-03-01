package parser

import (
	"bytes"
	"fmt"
	"strings"
	"time"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"github.com/google/gopacket/pcapgo"
)

// PcapParser handles network capture files.
type PcapParser struct{}

// Parse processes raw PCAP data and returns a human-readable summary of network flows.
func (p *PcapParser) Parse(data []byte) (string, error) {
	// Create a reader for the PCAP data
	reader, err := pcapgo.NewReader(bytes.NewReader(data))
	if err != nil {
		return "", fmt.Errorf("failed to create PCAP reader: %w", err)
	}

	var sb strings.Builder
	sb.WriteString("Network Traffic Summary (First 100 Packets):\n")
	sb.WriteString("Timestamp | Protocol | Source IP:Port -> Destination IP:Port | Payload Size\n")
	sb.WriteString("---------------------------------------------------------------------------\n")

	packetCount := 0
	maxPackets := 100 // Limit to avoid overwhelming the LLM

	for {
		data, ci, err := reader.ReadPacketData()
		if err != nil {
			break // End of file or error
		}

		packet := gopacket.NewPacket(data, layers.LayerTypeEthernet, gopacket.Default)

		// Extract layers
		ipLayer := packet.Layer(layers.LayerTypeIPv4)
		tcpLayer := packet.Layer(layers.LayerTypeTCP)
		udpLayer := packet.Layer(layers.LayerTypeUDP)

		if ipLayer != nil {
			ip, _ := ipLayer.(*layers.IPv4)
			srcIP := ip.SrcIP
			dstIP := ip.DstIP
			protocol := "Unknown"
			srcPort := "0"
			dstPort := "0"
			payloadSize := 0

			if tcpLayer != nil {
				tcp, _ := tcpLayer.(*layers.TCP)
				protocol = "TCP"
				srcPort = tcp.SrcPort.String()
				dstPort = tcp.DstPort.String()
				payloadSize = len(tcp.Payload)
			} else if udpLayer != nil {
				udp, _ := udpLayer.(*layers.UDP)
				protocol = "UDP"
				srcPort = udp.SrcPort.String()
				dstPort = udp.DstPort.String()
				payloadSize = len(udp.Payload)
			} else {
				protocol = ip.Protocol.String()
			}

			// Format: Timestamp | Protocol | Src:Port -> Dst:Port | Size
			timestamp := ci.Timestamp.Format(time.RFC3339)
			line := fmt.Sprintf("%s | %s | %s:%s -> %s:%s | %d bytes\n",
				timestamp, protocol, srcIP, srcPort, dstIP, dstPort, payloadSize)

			sb.WriteString(line)
			packetCount++
		}

		if packetCount >= maxPackets {
			sb.WriteString("\n... (Output truncated after 100 packets) ...\n")
			break
		}
	}

	if packetCount == 0 {
		return "No IPv4 packets found in PCAP file.", nil
	}

	return sb.String(), nil
}
