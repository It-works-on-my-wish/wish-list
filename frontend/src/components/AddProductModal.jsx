import React, { useState, useEffect } from 'react';
import { addProduct, scrapeAndAddProduct, listUserCategories,getSupportedPlatforms } from '../api';

const AddProductModal = ({ isOpen, onClose, onProductAdded }) => {
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    category_id: null,
    priority: 'low',
    check_frequency: 'daily',
    auto_track: true,
    current_price: '',
    target_price: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isScraping, setIsScraping] = useState(false);
  const [categories, setCategories] = useState([]);
  const TEST_USER_ID = "123e4567-e89b-12d3-a456-426614174000";
  const [supportedPlatforms, setSupportedPlatforms] = useState([]);
  


  const defaultFormData = {
    name: '',
    url: '',
    category_id: null,
    priority: 'low',
    check_frequency: 'daily',
    auto_track: true,
    current_price: '',
    target_price: '',
  };

  useEffect(() => {
    if (isOpen) {
      listUserCategories(TEST_USER_ID)
        .then(data => setCategories(data || []))
        .catch(err => console.error("Failed to load categories", err));
    }
  }, [isOpen]);
  useEffect(() => {
    getSupportedPlatforms()
      .then(data => setSupportedPlatforms(data.platforms))
      .catch(err => console.error("supported-platforms fetch failed:", err));
  }, []);
  

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  /**
   * Detect if a URL is a supported platform for auto-scraping.
   */

  const isKnownPlatform = (url) => {
    if (!url) return false;
    try {
      const hostname = new URL(url).hostname.toLowerCase();
      return supportedPlatforms.some(platform => hostname.includes(platform));
    } catch {
      return false;
    }
  };
  
  const isValidUrl = (url) => {
    if (!url) return false;
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };
  
  const urlValue = formData.url?.trim();
  const isKnown = isKnownPlatform(urlValue);
  const isValid = isValidUrl(urlValue);
  const isSupported = isKnown || isValid;
  const showManualPrice = urlValue && !isValid;

  /**
   * Auto-fetch: Uses the Factory + Strategy scraping endpoint.
   * Scrapes the URL and saves the product in one step.
   */
  const handleAutoFetch = async () => {
    if (!urlValue) {
      alert("Please enter a product URL first.");
      return;
    }
    

    setIsScraping(true);
    try {
      const rawCategoryId = formData.category_id || '';
      const isUuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(rawCategoryId);

      const scrapePayload = {
        url: urlValue,
        category_id: isUuid ? rawCategoryId : null,
        priority: formData.priority,
        check_frequency: formData.check_frequency,
        auto_track: formData.auto_track,
        target_price: formData.target_price ? parseFloat(formData.target_price) : null,
      };

      await scrapeAndAddProduct(TEST_USER_ID, scrapePayload);
      if (onProductAdded) {
        onProductAdded();
      }
      onClose();
      setFormData(defaultFormData);
    } catch (error) {
      console.error("Auto-fetch failed:", error);
      const message = error?.response?.data?.detail;
      alert(`Auto-fetch failed${message ? `: ${JSON.stringify(message)}` : '. Please try adding the product manually.'}`);
    } finally {
      setIsScraping(false);
    }
  };

  const handleSubmit = async () => {
    // If URL is from a supported platform, use the auto-fetch (scrape) flow
    if (urlValue && isValid) {
      handleAutoFetch();
      return;
    }

    // Manual add flow for unsupported platforms or no URL
    if (!formData.name) {
      alert("Product name is required.");
      return;
    }
    setIsSubmitting(true);
    try {
      const rawCategoryId = formData.category_id || '';
      const isUuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(rawCategoryId);
      const payload = {
        ...formData,
        name: formData.name.trim(),
        url: urlValue ? urlValue : null,
        category_id: isUuid ? rawCategoryId : null,
        current_price: formData.current_price ? parseFloat(formData.current_price) : null,
        target_price: formData.target_price ? parseFloat(formData.target_price) : null,
      };

      await addProduct(TEST_USER_ID, payload);
      if (onProductAdded) {
        onProductAdded();
      }
      onClose();
      setFormData(defaultFormData);
    } catch (error) {
      console.error("Failed to add product:", error);
      const message = error?.response?.data?.detail;
      alert(`Failed to add product${message ? `: ${JSON.stringify(message)}` : '.'}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isWorking = isSubmitting || isScraping;

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
                <button
                  type="button"
                  disabled={isWorking || !urlValue}
                  onClick={handleAutoFetch}
                  className="text-xs text-primary font-medium flex items-center gap-1 opacity-80 hover:opacity-100 cursor-pointer transition-all disabled:opacity-40 disabled:cursor-not-allowed hover:underline"
                >
                  {isScraping ? (
                    <>
                      <span className="material-symbols-outlined text-[14px] animate-spin">progress_activity</span>
                      Fetching...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-[14px]">auto_awesome</span>
                      Auto-fetch details
                    </>
                  )}
                </button>
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
                  placeholder="https://www.hepsiburada.com/product-p-XXXXX"
                />
              </div>
              {urlValue && isKnown && (
  <p className="text-xs text-emerald-500 mt-1.5 flex items-center gap-1">
    <span className="material-symbols-outlined text-[14px]">check_circle</span>
    Supported platform detected — use Auto-fetch to add instantly
  </p>
)}
{urlValue && !isKnown && isValid && (
  <p className="text-xs text-blue-500 mt-1.5 flex items-center gap-1">
    <span className="material-symbols-outlined text-[14px]">auto_awesome</span>
    Unknown platform — will try AI-powered fetch
  </p>
)}
{urlValue && !isValid && (
  <p className="text-xs text-amber-500 mt-1.5 flex items-center gap-1">
    <span className="material-symbols-outlined text-[14px]">info</span>
    Invalid URL — enter details manually below
  </p>
)}
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

            {/* Price inputs row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Current Price - shown when URL is unsupported or absent */}
              <label className="flex flex-col flex-1 group">
                <div className="flex items-center gap-2 pb-2">
                  <p className="text-slate-700 dark:text-slate-300 text-sm font-semibold group-focus-within:text-primary transition-colors">
                    Current Price (₺)
                  </p>
                  {isSupported && (
  <span className="text-[10px] text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-1.5 py-0.5 rounded font-medium">Optional</span>
)}
                </div>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 text-sm font-medium">₺</span>
                  <input
                    name="current_price"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.current_price}
                    onChange={handleChange}
                    disabled={false}
                    className="form-input flex w-full flex-1 rounded-lg text-slate-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary/50 border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#101922] focus:border-primary h-12 placeholder:text-slate-400 dark:placeholder:text-slate-500 pl-8 pr-4 text-base font-normal transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    placeholder={isSupported ? "Auto-fetched (leave empty)" : "Enter current price"}                  />
                </div>
                {!isSupported && !formData.current_price && (
                  <p className="text-xs text-slate-400 mt-1">Leave empty if unknown (will show as NaN)</p>
                )}
              </label>

              {/* Target Price - always shown */}
              <label className="flex flex-col flex-1 group">
                <p className="text-slate-700 dark:text-slate-300 text-sm font-semibold pb-2 group-focus-within:text-primary transition-colors">
                  Target Price (₺)
                </p>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 text-sm font-medium">₺</span>
                  <input
                    name="target_price"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.target_price}
                    onChange={handleChange}
                    className="form-input flex w-full flex-1 rounded-lg text-slate-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary/50 border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#101922] focus:border-primary h-12 placeholder:text-slate-400 dark:placeholder:text-slate-500 pl-8 pr-4 text-base font-normal transition-all"
                    placeholder="Set your target price"
                  />
                </div>
                <p className="text-xs text-slate-400 mt-1">Get notified when price drops below target</p>
              </label>
            </div>

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
            disabled={isWorking}
            onClick={onClose}
            className="px-5 py-2.5 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-200 dark:focus:ring-slate-700 transition-all active:scale-95 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            disabled={isWorking}
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
