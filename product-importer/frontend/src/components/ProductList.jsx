// Product table with pagination
import React, { useState, useEffect } from 'react';
import { productAPI } from '../services/api';
import ProductForm from './ProductForm';
import ConfirmDialog from './ConfirmDialog';

function ProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize, setPageSize] = useState(50);
  
  const [filters, setFilters] = useState({
    sku: '',
    name: '',
    description: '',
    active: '',
  });
  
  const [showForm, setShowForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [showDeleteAll, setShowDeleteAll] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, [page, pageSize, filters]);

  const fetchProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        size: pageSize,
        ...(filters.sku && { sku: filters.sku }),
        ...(filters.name && { name: filters.name }),
        ...(filters.description && { description: filters.description }),
        ...(filters.active !== '' && { active: filters.active === 'true' }),
      };

      const response = await productAPI.getProducts(params);
      setProducts(response.data.items);
      setTotalPages(response.data.pages);
      setTotalCount(response.data.total);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch products');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const handleCreate = () => {
    setEditingProduct(null);
    setShowForm(true);
  };

  const handleEdit = (product) => {
    setEditingProduct(product);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    try {
      await productAPI.deleteProduct(id);
      fetchProducts();
      setDeletingId(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete product');
    }
  };

  const handleDeleteAll = async () => {
    try {
      await productAPI.deleteAllProducts();
      fetchProducts();
      setShowDeleteAll(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete all products');
    }
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    setEditingProduct(null);
    fetchProducts();
  };

  return (
    <div className="product-list-container">
      <div className="list-header">
        <h2>Products ({totalCount})</h2>
        <div className="header-actions">
          <button onClick={handleCreate} className="btn btn-primary">
            Add Product
          </button>
          <button
            onClick={() => setShowDeleteAll(true)}
            className="btn btn-danger"
            disabled={totalCount === 0}
          >
            Delete All
          </button>
        </div>
      </div>

      <div className="filters">
        <input
          type="text"
          placeholder="Filter by SKU"
          value={filters.sku}
          onChange={(e) => handleFilterChange('sku', e.target.value)}
          className="filter-input"
        />
        <input
          type="text"
          placeholder="Filter by Name"
          value={filters.name}
          onChange={(e) => handleFilterChange('name', e.target.value)}
          className="filter-input"
        />
        <input
          type="text"
          placeholder="Filter by Description"
          value={filters.description}
          onChange={(e) => handleFilterChange('description', e.target.value)}
          className="filter-input"
        />
        <select
          value={filters.active}
          onChange={(e) => handleFilterChange('active', e.target.value)}
          className="filter-select"
        >
          <option value="">All Status</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading">Loading products...</div>
      ) : (
        <>
          <div className="table-container">
            <table className="product-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>SKU</th>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {products.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="no-data">
                      No products found
                    </td>
                  </tr>
                ) : (
                  products.map((product) => (
                    <tr key={product.id}>
                      <td>{product.id}</td>
                      <td className="sku-cell">{product.sku}</td>
                      <td>{product.name}</td>
                      <td className="description-cell">{product.description}</td>
                      <td>
                        <span className={`status-badge ${product.active ? 'active' : 'inactive'}`}>
                          {product.active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="actions-cell">
                        <button
                          onClick={() => handleEdit(product)}
                          className="btn btn-small btn-secondary"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => setDeletingId(product.id)}
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

          <div className="pagination">
            <div className="pagination-info">
              Showing {products.length > 0 ? ((page - 1) * pageSize) + 1 : 0} to{' '}
              {Math.min(page * pageSize, totalCount)} of {totalCount}
            </div>
            <div className="pagination-controls">
              <button
                onClick={() => setPage(1)}
                disabled={page === 1}
                className="btn btn-small"
              >
                First
              </button>
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="btn btn-small"
              >
                Previous
              </button>
              <span className="page-info">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages}
                className="btn btn-small"
              >
                Next
              </button>
              <button
                onClick={() => setPage(totalPages)}
                disabled={page === totalPages}
                className="btn btn-small"
              >
                Last
              </button>
              <select
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setPage(1);
                }}
                className="page-size-select"
              >
                <option value={25}>25 per page</option>
                <option value={50}>50 per page</option>
                <option value={100}>100 per page</option>
              </select>
            </div>
          </div>
        </>
      )}

      {showForm && (
        <ProductForm
          product={editingProduct}
          onClose={() => setShowForm(false)}
          onSuccess={handleFormSuccess}
        />
      )}

      {deletingId && (
        <ConfirmDialog
          title="Delete Product"
          message="Are you sure you want to delete this product? This action cannot be undone."
          onConfirm={() => handleDelete(deletingId)}
          onCancel={() => setDeletingId(null)}
        />
      )}

      {showDeleteAll && (
        <ConfirmDialog
          title="Delete All Products"
          message={`Are you sure you want to delete all ${totalCount} products? This action cannot be undone.`}
          onConfirm={handleDeleteAll}
          onCancel={() => setShowDeleteAll(false)}
          danger
        />
      )}
    </div>
  );
}

export default ProductList;
