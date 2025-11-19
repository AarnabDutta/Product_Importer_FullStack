// Main app component
import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ProductList from './components/ProductList';
import WebhookManager from './components/WebhookManager';

function App() {
  const [activeTab, setActiveTab] = useState('products');
  const [refreshProducts, setRefreshProducts] = useState(0);

  const handleUploadComplete = () => {
    setRefreshProducts(prev => prev + 1);
    setActiveTab('products');
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Product Importer</h1>
        <p>Import and manage products from CSV files</p>
      </header>

      <nav className="app-nav">
        <button
          className={`nav-btn ${activeTab === 'products' ? 'active' : ''}`}
          onClick={() => setActiveTab('products')}
        >
          Products
        </button>
        <button
          className={`nav-btn ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          Upload CSV
        </button>
        <button
          className={`nav-btn ${activeTab === 'webhooks' ? 'active' : ''}`}
          onClick={() => setActiveTab('webhooks')}
        >
          Webhooks
        </button>
      </nav>

      <main className="app-content">
        {activeTab === 'products' && (
          <ProductList key={refreshProducts} />
        )}
        {activeTab === 'upload' && (
          <FileUpload onUploadComplete={handleUploadComplete} />
        )}
        {activeTab === 'webhooks' && (
          <WebhookManager />
        )}
      </main>
    </div>
  );
}

export default App;
