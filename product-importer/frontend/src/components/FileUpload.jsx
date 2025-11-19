// File upload with progress bar
import React, { useState } from 'react';
import { uploadAPI } from '../services/api';
import { connectToProgressStream } from '../services/sse';

function FileUpload({ onUploadComplete }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingProgress, setProcessingProgress] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setError(null);
      setSuccess(false);
    } else {
      setError('Please select a valid CSV file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(false);
    setUploadProgress(0);
    setProcessingProgress(null);

    try {
      const response = await uploadAPI.uploadCSV(file, (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        setUploadProgress(percentCompleted);
      });

      const { task_id } = response.data;

      connectToProgressStream(
        task_id,
        (data) => {
          setProcessingProgress(data);
        },
        (data) => {
          setSuccess(true);
          setUploading(false);
          setTimeout(() => {
            if (onUploadComplete) onUploadComplete();
          }, 2000);
        },
        (error) => {
          setError(error.status || 'Processing failed');
          setUploading(false);
        }
      );
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
      setUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload CSV File</h2>
      <p className="upload-description">
        Upload a CSV file with product data. The file should contain columns: name, sku, description
      </p>

      <div className="upload-area">
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          disabled={uploading}
          className="file-input"
          id="file-upload"
        />
        <label htmlFor="file-upload" className="file-label">
          {file ? file.name : 'Choose CSV file'}
        </label>

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="btn btn-primary"
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </div>

      {uploading && uploadProgress < 100 && (
        <div className="progress-section">
          <h3>Uploading File...</h3>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <p className="progress-text">{uploadProgress}%</p>
        </div>
      )}

      {processingProgress && (
        <div className="progress-section">
          <h3>Processing Products...</h3>
          <div className="progress-bar">
            <div
              className="progress-fill processing"
              style={{ width: `${processingProgress.percent}%` }}
            />
          </div>
          <p className="progress-text">{processingProgress.percent}%</p>
          <p className="progress-status">{processingProgress.status}</p>
          <p className="progress-details">
            {processingProgress.current} / {processingProgress.total} products processed
          </p>
        </div>
      )}

      {error && (
        <div className="alert alert-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <strong>Success!</strong> Products imported successfully. Redirecting to product list...
        </div>
      )}
    </div>
  );
}

export default FileUpload;
