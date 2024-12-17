package app

import (
	"fmt"
	"io"
	"os"

	"github.com/pkg/sftp"
	"golang.org/x/crypto/ssh"
)

// DownloadDB connects to a remote server via SSH, removes the existing file if it exists, and downloads the file
func DownloadDB(host, user, password, remoteFilePath, localFilePath string) error {
	// Check if the local file exists
	if _, err := os.Stat(localFilePath); err == nil {
		// File exists, so remove it
		err := os.Remove(localFilePath)
		if err != nil {
			return fmt.Errorf("failed to remove existing local file: %v", err)
		}
		fmt.Printf("Existing file %s removed successfully\n", localFilePath)
	} else if !os.IsNotExist(err) {
		// If the error is not a "file does not exist" error, return it
		return fmt.Errorf("failed to check file existence: %v", err)
	}

	// SSH Client Configuration
	sshConfig := &ssh.ClientConfig{
		User: user,
		Auth: []ssh.AuthMethod{
			ssh.Password(password),
		},
		HostKeyCallback: ssh.InsecureIgnoreHostKey(),
	}

	// Connect to the SSH server
	conn, err := ssh.Dial("tcp", host+":22", sshConfig)
	if err != nil {
		return fmt.Errorf("failed to connect to SSH server: %v", err)
	}
	defer conn.Close()

	// Start SFTP session
	sftpClient, err := sftp.NewClient(conn)
	if err != nil {
		return fmt.Errorf("failed to create SFTP client: %v", err)
	}
	defer sftpClient.Close()

	// Open remote file
	remoteFile, err := sftpClient.Open(remoteFilePath)
	if err != nil {
		return fmt.Errorf("failed to open remote file: %v", err)
	}
	defer remoteFile.Close()

	// Create local file
	localFile, err := os.Create(localFilePath)
	if err != nil {
		return fmt.Errorf("failed to create local file: %v", err)
	}
	defer localFile.Close()

	// Copy remote file content to local file
	_, err = io.Copy(localFile, remoteFile)
	if err != nil {
		return fmt.Errorf("failed to copy file content: %v", err)
	}

	fmt.Printf("File %s copied to %s successfully\n", remoteFilePath, localFilePath)
	return nil
}
