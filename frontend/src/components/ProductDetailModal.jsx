import React, { useState } from 'react';
import { deleteProduct } from '../api';

const ProductDetailModal = ({ isOpen, onClose, product, onProductDeleted }) => {
  const [isDeleting, setIsDeleting] = useState(false);

  if (!isOpen || !product) return null;

  const handleDelete = async () => {
    if (window.confirm("Are you sure you want to abandon tracking this product?")) {
      setIsDeleting(true);
      try {
        await deleteProduct(product.id);
        if (onProductDeleted) onProductDeleted();
        onClose();
      } catch (error) {
        console.error("Failed to delete product:", error);
        alert("Failed to delete product");
      } finally {
        setIsDeleting(false);
      }
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm z-0" onClick={onClose}></div>
      <div className="relative z-10 bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-5xl flex flex-col max-h-[90vh] overflow-hidden border border-slate-200 dark:border-slate-700 animate-slide-up">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-700">
          <h2 className="text-xl font-bold">Product Details</h2>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 transition-colors rounded-full p-1 hover:bg-slate-100 dark:hover:bg-slate-700 active:scale-95">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        
        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Left Column: Product Image & Info */}
            <div className="w-full lg:w-1/3 flex flex-col gap-6">
              <div 
                className="w-full aspect-square rounded-xl bg-slate-100 dark:bg-slate-900 bg-center bg-no-repeat bg-contain border border-slate-200 dark:border-slate-700 hover:scale-[1.02] transition-transform duration-300"
                style={{ backgroundImage: `url("${product.url || 'https://placehold.co/400x400?text=No+Image'}")` }}
              ></div>
              <div>
                <h3 className="text-2xl font-bold mb-2 break-words leading-tight">{product.name}</h3>
                <p className="text-slate-600 dark:text-slate-400 text-sm capitalize">{product.priority} Priority</p>
              </div>
              <div className="flex flex-col gap-4 bg-slate-50 dark:bg-[#151f2b] p-4 rounded-lg border border-slate-200 dark:border-slate-700 transition-colors hover:border-slate-300 dark:hover:border-slate-600">
                <div className="flex justify-between items-center group">
                  <span className="text-slate-500 dark:text-slate-400 text-sm group-hover:text-primary transition-colors">Category</span>
                  <span className="font-medium">Tech</span>
                </div>
                <div className="flex justify-between items-center group">
                  <span className="text-slate-500 dark:text-slate-400 text-sm group-hover:text-primary transition-colors">Priority</span>
                  <span className={`font-medium px-2 py-1 rounded text-xs capitalize ${
                    product.priority === 'high' ? 'text-orange-600 dark:text-orange-400 bg-orange-100 dark:bg-orange-400/10' :
                    product.priority === 'medium' ? 'text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-400/10' :
                    'text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-400/10'
                  }`}>{product.priority}</span>
                </div>
                {product.auto_track && (
                  <div className="flex justify-between items-center group">
                    <span className="text-slate-500 dark:text-slate-400 text-sm group-hover:text-primary transition-colors">Check Frequency</span>
                    <span className="font-medium capitalize">{product.check_frequency}</span>
                  </div>
                )}
                <div className="flex justify-between items-center group">
                  <span className="text-slate-500 dark:text-slate-400 text-sm group-hover:text-primary transition-colors">Target Price</span>
                  <span className="font-bold text-green-600 dark:text-green-400">{product.target_price ? `$${product.target_price}` : 'Not set'}</span>
                </div>
              </div>
            </div>
            
            {/* Right Column: Price History */}
            <div className="w-full lg:w-2/3 flex flex-col gap-6">
              <div className="flex flex-col p-6 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-[#151f2b] h-full transition-all hover:shadow-md">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <p className="text-slate-600 dark:text-slate-400 text-sm font-medium mb-1">Current Price</p>
                    <p className="text-[32px] font-bold leading-tight">{product.current_price ? `$${product.current_price}` : 'Pending'}</p>
                  </div>
                  <div className="flex flex-col items-end">
                    {product.current_price && (
                      <div className="flex items-center gap-1 text-slate-500 bg-slate-50 dark:bg-slate-800 px-2 py-1 rounded-md">
                        <span className="text-sm font-medium">Tracking newly started</span>
                      </div>
                    )}
                  </div>
                </div>
                
                <p className="text-slate-700 dark:text-slate-300 text-base font-medium mb-4">Price History (Last 3 Months)</p>
                
                {/* Chart Area */}
                <div className="flex flex-col flex-1 min-h-[240px] relative">
                  {/* Y-Axis Labels */}
                  <div className="absolute left-0 top-0 bottom-8 w-12 flex flex-col justify-between text-xs text-slate-400">
                    <span>$400</span>
                    <span>$350</span>
                    <span>$300</span>
                    <span>$250</span>
                  </div>
                  {/* Chart Lines */}
                  <div className="absolute left-12 right-0 top-0 bottom-8 border-l border-b border-slate-200 dark:border-slate-700">
                    <div className="absolute inset-0 flex flex-col justify-between">
                      <div className="w-full border-t border-dashed border-slate-200 dark:border-slate-700/50"></div>
                      <div className="w-full border-t border-dashed border-slate-200 dark:border-slate-700/50"></div>
                      <div className="w-full border-t border-dashed border-slate-200 dark:border-slate-700/50"></div>
                    </div>
                    {/* Target Price Line */}
                    <div className="absolute w-full border-t-2 border-green-500/50 flex" style={{ top: '50%' }}>
                      <span className="absolute right-2 -top-5 text-xs text-green-600 dark:text-green-400 font-medium">Target: $299</span>
                    </div>
                    <svg className="absolute inset-0 h-full w-full" preserveAspectRatio="none" viewBox="0 0 100 100">
                      {/* Gradient Fill */}
                      <path d="M0,80 L20,75 L40,85 L60,40 L80,50 L100,20 L100,100 L0,100 Z" fill="url(#chart-gradient)" opacity="0.2"></path>
                      {/* Line */}
                      <path className="text-primary" d="M0,80 L20,75 L40,85 L60,40 L80,50 L100,20" fill="none" stroke="currentColor" strokeLinejoin="round" strokeWidth="2"></path>
                      <defs>
                        <linearGradient id="chart-gradient" x1="0" x2="0" y1="0" y2="1">
                          <stop className="text-primary" offset="0%" stopColor="currentColor" stopOpacity="1"></stop>
                          <stop className="text-primary" offset="100%" stopColor="currentColor" stopOpacity="0"></stop>
                        </linearGradient>
                      </defs>
                    </svg>
                  </div>
                  {/* X-Axis Labels */}
                  <div className="absolute left-12 right-0 bottom-0 h-8 flex justify-between items-end text-xs text-slate-400 px-2">
                    <span>Oct</span>
                    <span>Nov</span>
                    <span>Dec</span>
                    <span>Jan</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Modal Footer (Actions) */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50">
          <button 
            onClick={handleDelete}
            disabled={isDeleting}
            className="text-red-600 hover:text-red-700 dark:text-red-500 dark:hover:text-red-400 text-sm font-medium transition-colors flex items-center gap-2 hover:bg-red-50 dark:hover:bg-red-900/20 px-3 py-2 rounded-lg active:scale-95 disabled:opacity-50"
          >
            <span className="material-symbols-outlined text-sm">delete</span>
            {isDeleting ? 'Deleting...' : 'Abandon Tracking'}
          </button>
          <div className="flex gap-3">
            <button className="px-5 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 text-sm font-medium transition-all flex items-center gap-2 active:scale-95">
              <span className="material-symbols-outlined text-sm">edit</span>
              Edit Details
            </button>
            <button className="px-6 py-2.5 rounded-lg bg-primary hover:bg-primary/90 text-white text-sm font-medium transition-all flex items-center gap-2 shadow-sm focus:ring-2 focus:ring-primary/50 active:scale-95 hover:shadow-primary/30">
              <span className="material-symbols-outlined text-sm">shopping_cart</span>
              Purchase Now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailModal;
