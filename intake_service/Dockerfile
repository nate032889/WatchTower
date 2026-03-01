# Stage 1: Build the Go binary
FROM golang:1.23-alpine AS builder

WORKDIR /app

# Install dependencies for CGO/parsers if needed (like tshark for pcaps later)
RUN apk add --no-cache gcc musl-dev

# Download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest of the source code
COPY . .

# Build the binary
RUN CGO_ENABLED=0 GOOS=linux go build -o intake-service .

# Stage 2: Create a minimal runner image
FROM alpine:latest

WORKDIR /app

# Install CA certificates for external HTTPS calls and any required runtime tools
RUN apk add --no-cache ca-certificates

# Copy the built binary from the builder stage
COPY --from=builder /app/intake-service .

EXPOSE 3000

# Run the binary
CMD ["./intake-service"]