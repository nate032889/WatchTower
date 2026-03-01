package data

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"log"
	"os"
	"strings"

	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
)

// MinioRepository defines the interface for data access.
type MinioRepository interface {
	GetObject(objectKey string) ([]byte, error)
	SaveObject(objectKey string, data []byte, contentType string) error
}

type minioRepository struct {
	client     *minio.Client
	bucketName string
}

// NewMinioRepository initializes and returns a new Minio repository.
func NewMinioRepository() (MinioRepository, error) {
	endpoint := os.Getenv("MINIO_ENDPOINT")
	accessKey := os.Getenv("MINIO_ACCESS_KEY")
	secretKey := os.Getenv("MINIO_SECRET_KEY")
	bucketName := os.Getenv("MINIO_BUCKET_NAME")
	useSSL := !strings.Contains(endpoint, "localhost")

	if endpoint == "" || accessKey == "" || secretKey == "" || bucketName == "" {
		return nil, fmt.Errorf("MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, and MINIO_BUCKET_NAME must be set")
	}

	minioClient, err := minio.New(endpoint, &minio.Options{
		Creds:  credentials.NewStaticV4(accessKey, secretKey, ""),
		Secure: useSSL,
	})
	if err != nil {
		return nil, err
	}

	log.Println("Successfully connected to Minio.")
	return &minioRepository{client: minioClient, bucketName: bucketName}, nil
}

// GetObject retrieves the raw bytes of an object from Minio.
func (r *minioRepository) GetObject(objectKey string) ([]byte, error) {
	obj, err := r.client.GetObject(context.Background(), r.bucketName, objectKey, minio.GetObjectOptions{})
	if err != nil {
		return nil, fmt.Errorf("failed to initiate object retrieval: %w", err)
	}
	defer obj.Close()

	data, err := io.ReadAll(obj)
	if err != nil {
		return nil, fmt.Errorf("failed to read object data: %w", err)
	}

	return data, nil
}

// SaveObject uploads an object to Minio.
func (r *minioRepository) SaveObject(objectKey string, data []byte, contentType string) error {
	reader := bytes.NewReader(data)
	_, err := r.client.PutObject(context.Background(), r.bucketName, objectKey, reader, int64(len(data)), minio.PutObjectOptions{ContentType: contentType})
	if err != nil {
		return fmt.Errorf("failed to upload object '%s': %w", objectKey, err)
	}
	return nil
}
