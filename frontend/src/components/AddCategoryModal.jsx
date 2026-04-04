import React, { useState } from 'react';
import { addNewCategory } from '../api';

const CATEGORY_TYPES = [
  { value: 'COSMETICS', label: 'Cosmetics', icon: 'face' },
  { value: 'CLOTHING', label: 'Clothing', icon: 'checkroom' },
  { value: 'TECHNOLOGY', label: 'Technology', icon: 'devices' },
  { value: 'KITCHEN', label: 'Kitchen', icon: 'kitchen' },
  { value: 'CUSTOM', label: 'Custom', icon: 'category' },
];

const TEST_USER_ID = "123e4567-e89b-12d3-a456-426614174000";

const AddCategoryModal = ({ isOpen, onClose, onCategoryAdded }) => {
  const [name, setName] = useState('');
  const [categoryType, setCategoryType] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleClose = () => {
    setName('');
    setCategoryType('');
    setError('');
    onClose();
  };

  const handleSubmit = async () => {
    if (!name.trim()) {
      setError('Please enter a category name.');
      return;
    }
    if (!categoryType) {
      setError('Please select a category type.');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      await addNewCategory(TEST_USER_ID, { name: name.trim(), category_type: categoryType });
      if (onCategoryAdded) onCategoryAdded();
      handleClose();
    } catch (err) {
      if (err.response?.status === 400) {
        setError('A category with this name already exists.');
      } else {
        setError('Failed to create category. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm z-0" onClick={handleClose}></div>
      <div className="relative z-10 bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-md flex flex-col overflow-hidden border border-slate-200 dark:border-slate-700 animate-slide-up">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg text-primary">
              <span className="material-symbols-outlined text-[20px]">create_new_folder</span>
            </div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">New Category</h2>
          </div>
          <button
            onClick={handleClose}
            className="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 transition-colors rounded-full p-1 hover:bg-slate-100 dark:hover:bg-slate-700 active:scale-95"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Body */}
        <div className="flex flex-col gap-6 p-6">

          {/* Name input */}
          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
              Category Name
            </label>
            <input
              type="text"
              value={name}
              onChange={e => { setName(e.target.value); setError(''); }}
              placeholder="e.g. Running Gear"
              className="w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
            />
          </div>

          {/* Category type selector */}
          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
              Category Type
            </label>
            <div className="grid grid-cols-3 gap-2">
              {CATEGORY_TYPES.map(type => (
                <button
                  key={type.value}
                  onClick={() => { setCategoryType(type.value); setError(''); }}
                  className={`flex flex-col items-center gap-1.5 py-3 px-2 rounded-lg border transition-all duration-200 active:scale-95 text-xs font-semibold
                    ${categoryType === type.value
                      ? 'bg-primary text-white border-primary shadow-md shadow-primary/20'
                      : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:border-primary/50 hover:text-primary'
                    }`}
                >
                  <span className="material-symbols-outlined text-[20px]">{type.icon}</span>
                  {type.label}
                </button>
              ))}
            </div>
          </div>

          {/* Error message */}
          {error && (
            <div className="flex items-center gap-2 px-4 py-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700/50 text-red-600 dark:text-red-400 text-sm">
              <span className="material-symbols-outlined text-[18px]">error</span>
              {error}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50">
          <button
            onClick={handleClose}
            className="px-5 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 text-sm font-medium transition-all active:scale-95"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="px-6 py-2.5 rounded-lg bg-primary hover:bg-primary/90 text-white text-sm font-semibold transition-all flex items-center gap-2 shadow-sm hover:shadow-primary/30 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="material-symbols-outlined text-sm">add</span>
            {isSubmitting ? 'Creating...' : 'Create Category'}
          </button>
        </div>

      </div>
    </div>
  );
};

export default AddCategoryModal;