// Webhook CRUD interface
import React, { useState, useEffect } from 'react';
import { webhookAPI } from '../services/api';
import ConfirmDialog from './ConfirmDialog';

function WebhookManager() {
  const [webhooks, setWebhooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingWebhook, setEditingWebhook] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [testingId, setTestingId] = useState(null);
  const [testResult, setTestResult] = useState(null);

  const [formData, setFormData] = useState({
    url: '',
    event_type: 'product.imported',
    enabled: true,
  });

  useEffect(() => {
    fetchWebhooks();
  }, []);

  const fetchWebhooks = async () => {
    setLoading(true);
    try {
      const response = await webhookAPI.getWebhooks();
      setWebhooks(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch webhooks');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingWebhook(null);
    setFormData({
      url: '',
      event_type: 'product.imported',
      enabled: true,
    });
    setShowForm(true);
  };

  const handleEdit = (webhook) => {
    setEditingWebhook(webhook);
    setFormData({
      url: webhook.url,
      event_type: webhook.event_type,
      enabled: webhook.enabled,
    });
    setShowForm(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      if (editingWebhook) {
        await webhookAPI.updateWebhook(editingWebhook.id, formData);
      } else {
        await webhookAPI.createWebhook(formData);
      }
      setShowForm(false);
      fetchWebhooks();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save webhook');
    }
  };

  const handleDelete = async (id) => {
    try {
      await webhookAPI.deleteWebhook(id);
      fetchWebhooks();
      setDeletingId(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete webhook');
    }
  };

  const handleTest = async (id) => {
    setTestingId(id);
    setTestResult(null);
    try {
      const response = await webhookAPI.testWebhook(id);
      setTestResult(response.data);
    } catch (err) {
      setTestResult({
        success: false,
        error: err.response?.data?.detail || 'Test failed',
      });
    } finally {
      setTestingId(null);
    }
  };

  return (
    <div className="webhook-container">
      <div className="list-header">
        <h2>Webhook Configuration</h2>
        <button onClick={handleCreate} className="btn btn-primary">
          Add Webhook
        </button>
      </div>

      {error && (
        <div className="alert alert-error">{error}</div>
      )}

      {testResult && (
        <div className={`alert ${testResult.success ? 'alert-success' : 'alert-error'}`}>
          {testResult.success ? (
            <>
              <strong>Test Successful!</strong>
              <br />
              Status Code: {testResult.status_code}
              <br />
              Response Time: {testResult.response_time}s
            </>
          ) : (
            <>
              <strong>Test Failed:</strong> {testResult.error}
            </>
          )}
          <button
            onClick={() => setTestResult(null)}
            className="close-btn"
            style={{ float: 'right' }}
          >
            &times;
          </button>
        </div>
      )}

      {loading ? (
        <div className="loading">Loading webhooks...</div>
      ) : (
        <div className="table-container">
          <table className="product-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>URL</th>
                <th>Event Type</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {webhooks.length === 0 ? (
                <tr>
                  <td colSpan="5" className="no-data">
                    No webhooks configured
                  </td>
                </tr>
              ) : (
                webhooks.map((webhook) => (
                  <tr key={webhook.id}>
                    <td>{webhook.id}</td>
                    <td className="url-cell">{webhook.url}</td>
                    <td>{webhook.event_type}</td>
                    <td>
                      <span className={`status-badge ${webhook.enabled ? 'active' : 'inactive'}`}>
                        {webhook.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </td>
                    <td className="actions-cell">
                      <button
                        onClick={() => handleTest(webhook.id)}
                        className="btn btn-small btn-secondary"
                        disabled={testingId === webhook.id}
                      >
                        {testingId === webhook.id ? 'Testing...' : 'Test'}
                      </button>
                      <button
                        onClick={() => handleEdit(webhook)}
                        className="btn btn-small btn-secondary"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => setDeletingId(webhook.id)}
                        className="btn btn-small btn-danger"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingWebhook ? 'Edit Webhook' : 'Create Webhook'}</h2>
              <button onClick={() => setShowForm(false)} className="close-btn">
                &times;
              </button>
            </div>

            <form onSubmit={handleSubmit} className="product-form">
              <div className="form-group">
                <label htmlFor="url">Webhook URL *</label>
                <input
                  type="url"
                  id="url"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  required
                  placeholder="https://example.com/webhook"
                />
              </div>

              <div className="form-group">
                <label htmlFor="event_type">Event Type *</label>
                <select
                  id="event_type"
                  value={formData.event_type}
                  onChange={(e) => setFormData({ ...formData, event_type: e.target.value })}
                  required
                >
                  <option value="product.imported">Product Imported</option>
                  <option value="product.created">Product Created</option>
                  <option value="product.updated">Product Updated</option>
                  <option value="product.deleted">Product Deleted</option>
                </select>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.enabled}
                    onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                  />
                  <span>Enabled</span>
                </label>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {deletingId && (
        <ConfirmDialog
          title="Delete Webhook"
          message="Are you sure you want to delete this webhook?"
          onConfirm={() => handleDelete(deletingId)}
          onCancel={() => setDeletingId(null)}
        />
      )}
    </div>
  );
}

export default WebhookManager;
