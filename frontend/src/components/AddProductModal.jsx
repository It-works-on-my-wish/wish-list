import React, { useState, useEffect } from 'react';
import { addProduct, listUserCategories } from '../api';

const AddProductModal = ({ isOpen, onClose, onProductAdded }) => {
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    category_id: null, // Depending on if category fetching is complete, can be null
    priority: 'low',
    check_frequency: 'daily',
    auto_track: true
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [categories, setCategories] = useState([]);
  const TEST_USER_ID = "123e4567-e89b-12d3-a456-426614174000";

  useEffect(() => {
    if (isOpen) {
      listUserCategories(TEST_USER_ID)
        .then(data => setCategories(data || []))
        .catch(err => console.error("Failed to load categories", err));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async () => {
    if (!formData.name) {
      alert("Product name is required.");
      return;
    }
    setIsSubmitting(true);
    try {
      await addProduct(TEST_USER_ID, formData);
      if (onProductAdded) {
        onProductAdded();
      }
      onClose();
      // Reset form on success
      setFormData({
         name: '',
         url: '',
         category_id: null,
         priority: 'low',
         check_frequency: 'daily',
         auto_track: true
      });
    } catch (error) {
       console.error("Failed to add product:", error);
       alert("Failed to add product.");
    } finally {
       setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-slate-900/40 dark:bg-black/60 backdrop-blur-sm z-0" onClick={onClose}></div>
      <div className="relative z-10 w-full max-w-2xl bg-white dark:bg-[#1a2332] rounded-xl shadow-2xl flex flex-col overflow-hidden border border-slate-200 dark:border-slate-800 animate-slide-up">
        
        <div className="px-6 py-5 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center bg-slate-50 dark:bg-[#1a2332]">
          <h3 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">add_shopping_cart</span>
            Add to Wishlist
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors p-1 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 active:scale-95">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        
        <div className="px-8 py-6 flex-1 overflow-y-auto space-y-6">
          <div className="space-y-6">
            <label className="flex flex-col flex-1 group">
              <div className="flex items-center justify-between pb-2">
                <p className="text-slate-700 dark:text-slate-300 text-sm font-semibold group-focus-within:text-primary transition-colors">Product URL</p>
                <span className="text-xs text-primary font-medium flex items-center gap-1 opacity-80 hover:opacity-100 cursor-pointer transition-opacity">
                  <span className="material-symbols-outlined text-[14px]">auto_awesome</span> Auto-fetch details
                </span>
              </div>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none transition-colors group-focus-within:text-primary">
                  <span className="material-symbols-outlined text-slate-400">link</span>
                </span>
                <input 
                  name="url"
                  value={formData.url}
                  onChange={handleChange}
                  className="form-input flex w-full flex-1 rounded-lg text-slate-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary/50 border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#101922] focus:border-primary h-12 placeholder:text-slate-400 dark:placeholder:text-slate-500 pl-10 pr-4 text-base font-normal transition-all" 
                  placeholder="https://store.example.com/item" 
                />
              </div>
            </label>
            
            <label className="flex flex-col flex-1 group">
              <p className="text-slate-700 dark:text-slate-300 text-sm font-semibold pb-2 group-focus-within:text-primary transition-colors">Product Name</p>
              <input 
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="form-input flex w-full flex-1 rounded-lg text-slate-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary/50 border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#101922] focus:border-primary h-12 placeholder:text-slate-400 dark:placeholder:text-slate-500 px-4 text-base font-normal transition-all" 
                placeholder="Enter product name manually" 
              />
            </label>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <label className="flex flex-col flex-1 group">
                <p className="text-slate-700 dark:text-slate-300 text-sm font-semibold pb-2 group-focus-within:text-primary transition-colors">Category</p>
                <select 
                  name="category_id"
                  value={formData.category_id || ''}
                  onChange={handleChange}
                  className="form-input appearance-none flex w-full flex-1 rounded-lg text-slate-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary/50 border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#101922] focus:border-primary h-12 placeholder:text-slate-400 px-4 text-base font-normal transition-all"
                >
                  <option disabled value="">Select category</option>
                  {categories.map(cat => (
                     <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </label>
              
              <label className="flex flex-col flex-1 group">
                <p className="text-slate-700 dark:text-slate-300 text-sm font-semibold pb-2 group-focus-within:text-primary transition-colors">Priority</p>
                <select 
                  name="priority"
                  value={formData.priority}
                  onChange={handleChange}
                  className="form-input appearance-none flex w-full flex-1 rounded-lg text-slate-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary/50 border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#101922] focus:border-primary h-12 placeholder:text-slate-400 px-4 text-base font-normal transition-all"
                 >
                  <option value="high">High - Need it soon</option>
                  <option value="medium">Medium - Whenever</option>
                  <option value="low">Low - Just looking</option>
                </select>
              </label>
            </div>
            
            <div className="bg-slate-50 dark:bg-[#101922]/50 rounded-xl p-5 border border-slate-200 dark:border-slate-800 transition-colors hover:border-slate-300 dark:hover:border-slate-700">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-slate-800 dark:text-white text-base font-semibold flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary animate-pulse">monitoring</span>
                    Price Tracking
                  </p>
                  <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">Automatically check for price drops</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input 
                     type="checkbox" 
                     name="auto_track"
                     checked={formData.auto_track}
                     onChange={handleChange}
                     className="sr-only peer" 
                  />
                  <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/30 dark:peer-focus:ring-primary/20 rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                </label>
              </div>
              
              <div className="pt-4 border-t border-slate-200 dark:border-slate-700/50">
                <p className="text-slate-700 dark:text-slate-300 text-sm font-semibold pb-3">Check Frequency</p>
                <div className="flex gap-3">
                  <label className="flex-1 cursor-pointer">
                    <input 
                      className="peer sr-only" 
                      name="check_frequency" 
                      type="radio" 
                      value="hourly" 
                      checked={formData.check_frequency === 'hourly'}
                      onChange={handleChange}
                    />
                    <div className="text-center px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-lg text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 peer-checked:border-primary peer-checked:bg-primary/10 peer-checked:text-primary transition-all active:scale-95">
                      Hourly
                    </div>
                  </label>
                  <label className="flex-1 cursor-pointer">
                    <input 
                       className="peer sr-only" 
                       name="check_frequency" 
                       type="radio" 
                       value="daily" 
                       checked={formData.check_frequency === 'daily'}
                       onChange={handleChange}
                    />
                    <div className="text-center px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-lg text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 peer-checked:border-primary peer-checked:bg-primary/10 peer-checked:text-primary transition-all font-medium active:scale-95">
                      Daily
                    </div>
                  </label>
                  <label className="flex-1 cursor-pointer">
                    <input 
                       className="peer sr-only" 
                       name="check_frequency" 
                       type="radio" 
                       value="weekly" 
                       checked={formData.check_frequency === 'weekly'}
                       onChange={handleChange}
                    />
                    <div className="text-center px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-lg text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 peer-checked:border-primary peer-checked:bg-primary/10 peer-checked:text-primary transition-all active:scale-95">
                      Weekly
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#1a2332] flex justify-end gap-3">
          <button 
            disabled={isSubmitting} 
            onClick={onClose} 
            className="px-5 py-2.5 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-200 dark:focus:ring-slate-700 transition-all active:scale-95 disabled:opacity-50"
          >
            Cancel
          </button>
          <button 
            disabled={isSubmitting}
            onClick={handleSubmit}
            className="px-5 py-2.5 rounded-lg text-sm font-medium text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all shadow-sm flex items-center gap-2 active:scale-95 hover:shadow-primary/30 disabled:opacity-50"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            {isSubmitting ? 'Adding...' : 'Add to Wishlist'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddProductModal;
