package data

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"log"
	"strings"

	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
)

// MinioRepository defines the interface for data access.
type MinioRepository interface {
	GetObject(ctx context.Context, objectKey string) ([]byte, error)
	SaveObject(ctx context.Context, objectKey string, data []byte, contentType string) error
}

type minioRepository struct {
	client     *minio.Client
	bucketName string
}

// NewMinioRepository initializes and returns a new Minio repository.
// It now receives its configuration instead of reading it globally.
func NewMinioRepository(endpoint, accessKey, secretKey, bucketName string) (MinioRepository, error) {
	useSSL := !strings.Contains(endpoint, "localhost")

	minioClient, err := minio.New(endpoint, &minio.Options{
		Creds:  credentials.NewStaticV4(accessKey, secretKey, ""),
		Secure: useSSL,
	})
	if err != nil {
		return nil, err
	}

	// Ensure the bucket exists
	ctx := context.Background()
	exists, err := minioClient.BucketExists(ctx, bucketName)
	if err != nil {
		return nil, fmt.Errorf("failed to check if bucket exists: %w", err)
	}
	if !exists {
		log.Printf("Bucket %s does not exist, creating it...", bucketName)
		err = minioClient.MakeBucket(ctx, bucketName, minio.MakeBucketOptions{})
		if err != nil {
			return nil, fmt.Errorf("failed to create bucket: %w", err)
		}
	}

	log.Println("Successfully connected to Minio.")
	return &minioRepository{client: minioClient, bucketName: bucketName}, nil
}

// GetObject retrieves the raw bytes of an object from Minio.
func (r *minioRepository) GetObject(ctx context.Context, objectKey string) ([]byte, error) {
	obj, err := r.client.GetObject(ctx, r.bucketName, objectKey, minio.GetObjectOptions{})
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
func (r *minioRepository) SaveObject(ctx context.Context, objectKey string, data []byte, contentType string) error {
	reader := bytes.NewReader(data)
	_, err := r.client.PutObject(ctx, r.bucketName, objectKey, reader, int64(len(data)), minio.PutObjectOptions{ContentType: contentType})
	if err != nil {
		return fmt.Errorf("failed to upload object '%s': %w", objectKey, err)
	}
	return nil
}
