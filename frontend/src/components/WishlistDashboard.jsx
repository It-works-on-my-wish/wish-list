import React, { useState, useEffect } from 'react';
import AddProductModal from './AddProductModal';
import ProductDetailModal from './ProductDetailModal';
import { getUserProducts, listUserCategories, getUserStats} from '../api';

const WishlistDashboard = () => {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
const [selectedCategory, setSelectedCategory] = useState(null);
const filteredProducts = selectedCategory
  ? products.filter(p => p.category_id === selectedCategory)
  : products;

  const TEST_USER_ID = "123e4567-e89b-12d3-a456-426614174000";
  const [stats, setStats] = useState({ tracked: 0, purchased: 0, total_savings: 0, price_drops_today: 0 });

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const data = await getUserProducts(TEST_USER_ID);
      setProducts(data || []);
    } catch (error) {
      console.error("Failed to fetch products:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    getUserStats(TEST_USER_ID)
      .then(data => setStats(data))
      .catch(err => console.error("Failed to load stats", err));
  }, []);

  useEffect(() => {
    fetchProducts();
  }, []);

  useEffect(() => {
    listUserCategories(TEST_USER_ID)
      .then(data => setCategories(data || []))
      .catch(err => console.error("Failed to load categories", err));
  }, []);

  useEffect(() => {
    console.log("Fetching categories...");
    listUserCategories(TEST_USER_ID)
      .then(data => {
        console.log("Categories:", data);
        setCategories(data || []);
      })
      .catch(err => console.error("Failed to load categories", err));
  }, []);

  const handleOpenDetail = (product) => {
    setSelectedProduct(product);
    setIsDetailModalOpen(true);
  };

  return (
    <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-8 animate-fade-in">
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Tracked Items */}
        <div className="group flex flex-col gap-3 rounded-xl p-6 bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
          <div className="flex justify-between items-start">
            <p className="text-slate-500 dark:text-slate-400 text-sm font-semibold uppercase tracking-wider">Tracked Items</p>
            <div className="p-2 bg-primary/10 rounded-lg text-primary group-hover:bg-primary group-hover:text-white transition-colors duration-300">
              <span className="material-symbols-outlined text-[20px]">list_alt</span>
            </div>
          </div>
          <p className="text-slate-900 dark:text-white text-3xl font-bold leading-tight">{stats.tracked}</p>
          <div className="flex items-center gap-1.5 mt-1">
            <span className="material-symbols-outlined text-green-500 text-[16px]">trending_up</span>
            <p className="text-green-500 text-sm font-semibold">+5% <span className="text-slate-400 dark:text-slate-500 font-medium">this month</span></p>
          </div>
        </div>

        {/* Total Savings */}
        <div className="group flex flex-col gap-3 rounded-xl p-6 bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
          <div className="flex justify-between items-start">
            <p className="text-slate-500 dark:text-slate-400 text-sm font-semibold uppercase tracking-wider">Total Savings</p>
            <div className="p-2 bg-green-500/10 rounded-lg text-green-500 group-hover:bg-green-500 group-hover:text-white transition-colors duration-300">
              <span className="material-symbols-outlined text-[20px]">savings</span>
            </div>
          </div>
          <p className="text-slate-900 dark:text-white text-3xl font-bold leading-tight">₺{stats.total_savings.toLocaleString()}</p>
          <div className="flex items-center gap-1.5 mt-1">
            <span className="material-symbols-outlined text-green-500 text-[16px]">trending_up</span>
            <p className="text-green-500 text-sm font-semibold">+$45.20 <span className="text-slate-400 dark:text-slate-500 font-medium">this month</span></p>
          </div>
        </div>

        {/* Price Drops */}
        <div className="group flex flex-col gap-3 rounded-xl p-6 bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
          <div className="flex justify-between items-start">
            <p className="text-slate-500 dark:text-slate-400 text-sm font-semibold uppercase tracking-wider">Price Drops Today</p>
            <div className="p-2 bg-amber-500/10 rounded-lg text-amber-500 group-hover:bg-amber-500 group-hover:text-white transition-colors duration-300">
              <span className="material-symbols-outlined text-[20px]">sell</span>
            </div>
          </div>
          <p className="text-slate-900 dark:text-white text-3xl font-bold leading-tight">{stats.price_drops_today}</p>
          <div className="flex items-center gap-1.5 mt-1">
            <span className="material-symbols-outlined text-amber-500 text-[16px] animate-pulse">local_fire_department</span>
            <p className="text-amber-500 text-sm font-semibold">Hot deals waiting!</p>
          </div>
        </div>

        {/* Purchased */}
        <div className="group flex flex-col gap-3 rounded-xl p-6 bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
          <div className="flex justify-between items-start">
            <p className="text-slate-500 dark:text-slate-400 text-sm font-semibold uppercase tracking-wider">Purchased</p>
            <div className="p-2 bg-purple-500/10 rounded-lg text-purple-500 group-hover:bg-purple-500 group-hover:text-white transition-colors duration-300">
              <span className="material-symbols-outlined text-[20px]">shopping_cart_checkout</span>
            </div>
          </div>
          <p className="text-slate-900 dark:text-white text-3xl font-bold leading-tight">{stats.purchased}</p>          <div className="flex items-center gap-1.5 mt-1">
            <span className="material-symbols-outlined text-slate-400 dark:text-slate-500 text-[16px]">check_circle</span>
            <p className="text-slate-400 dark:text-slate-500 text-sm font-semibold">Total lifetime</p>
          </div>
        </div>
      </section>

      {/* Items Section */}
      <section className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold leading-tight relative inline-block after:content-[''] after:absolute after:-bottom-1 after:left-0 after:w-1/2 after:h-1 after:bg-primary after:rounded-full">Your Tracked Items</h2>
          <div className="flex gap-2">
            <button className="p-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 transition-all duration-200 hover:shadow-md active:scale-95">
              <span className="material-symbols-outlined text-[20px]">grid_view</span>
            </button>
            <button className="p-2 rounded-lg border border-transparent text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all duration-200 hover:shadow-md active:scale-95">
              <span className="material-symbols-outlined text-[20px]">view_list</span>
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide -mx-4 px-4 sm:mx-0 sm:px-0">
        <button
  onClick={() => setSelectedCategory(null)}
  className={`flex h-9 shrink-0 items-center justify-center rounded-full px-5 transition-all duration-300 active:scale-95 text-sm font-bold
    ${selectedCategory === null
      ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-900'
      : 'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:opacity-90'
    }`}
>
  All Items
</button>
          
{categories.map(cat => (
  <button
    key={cat.id}
    onClick={() => setSelectedCategory(cat.id)}
    className={`flex h-9 shrink-0 items-center justify-center rounded-full border transition-all duration-300 px-5 active:scale-95 text-sm font-semibold
      ${selectedCategory === cat.id
        ? 'bg-primary text-white border-primary'
        : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-primary/10 hover:text-primary hover:border-primary/30'
      }`}
  >
    {cat.name}
  </button>
))}
          <button 
            onClick={() => setIsAddModalOpen(true)}
            className="flex h-9 shrink-0 items-center justify-center rounded-full bg-primary text-white hover:bg-primary/90 transition-all duration-300 px-4 gap-1 shadow-sm hover:shadow-primary/30 active:scale-95"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            <p className="text-sm font-semibold">New Item</p>
          </button>
          <button className="flex h-9 shrink-0 items-center justify-center rounded-full border border-dashed border-slate-300 dark:border-slate-600 text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all duration-300 px-4 gap-1 active:scale-95 hover:border-solid hover:border-slate-400">
            <span className="material-symbols-outlined text-[18px]">filter_list</span>
            <p className="text-sm font-semibold">Filter</p>
          </button>
        </div>

        {/* Items Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-2">
          
          {loading ? (
             <div className="col-span-full py-12 flex justify-center text-slate-500">Loading products...</div>
          ) : products.length === 0 ? (
             <div className="col-span-full py-12 flex flex-col items-center justify-center text-slate-500 gap-4">
                <span className="material-symbols-outlined text-4xl opacity-50">inventory_2</span>
                <p>No items tracked yet. Add your first item!</p>
             </div>
          ) : (
            filteredProducts.map((product) => (
              <div key={product.id} className={`flex flex-col rounded-xl overflow-hidden bg-white dark:bg-slate-800/80 border shadow-sm hover:shadow-xl transition-all duration-500 group relative hover:-translate-y-2 ${product.purchase_state === 'purchased' ? 'border-green-300 dark:border-green-700/60' : 'border-slate-200 dark:border-slate-700/80'}`}>
                {/* Status Badge */}
                <div className={`absolute top-3 left-3 z-10 px-2.5 py-1 rounded-full text-xs font-bold backdrop-blur-sm shadow-sm flex items-center gap-1 ${product.purchase_state === 'purchased' ? 'bg-green-500/90 text-white' : 'bg-amber-400/90 text-amber-900'}`}>
                  <span className="material-symbols-outlined text-[14px]">{product.purchase_state === 'purchased' ? 'check_circle' : 'schedule'}</span>
                  {product.purchase_state === 'purchased' ? 'Purchased' : 'Pending'}
                </div>
                <button className="absolute top-3 right-3 z-10 p-2 rounded-full bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm text-slate-400 hover:text-red-500 hover:bg-white dark:hover:bg-slate-900 transition-all duration-300 shadow-sm hover:scale-110 active:scale-90">
                  <span className="material-symbols-outlined text-[20px] fill-current">favorite</span>
                </button>
                <div 
                  className="w-full h-48 bg-slate-100 dark:bg-slate-900 bg-center bg-no-repeat bg-contain p-4 group-hover:scale-110 transition-transform duration-700" 
                  style={{backgroundImage: `url("${product.image_url || 'https://placehold.co/400x400?text=No+Image'}")`}}
                ></div>
                <div className="flex flex-col flex-1 p-5 gap-4 relative bg-white dark:bg-slate-800/80 z-10">
                  <div>
                    <h3 className="text-slate-900 dark:text-white text-lg font-bold leading-tight line-clamp-1 mb-1 group-hover:text-primary transition-colors">{product.name}</h3>
                    <p className="text-slate-500 dark:text-slate-400 text-sm capitalize">{product.priority} Priority</p>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex flex-col">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl font-bold text-slate-900 dark:text-white">
                          {product.current_price != null ? `₺${product.current_price.toLocaleString()}` : "NaN"}
                        </span>
                      </div>
                      {product.target_price != null && (
                        <p className="text-amber-500 text-xs font-semibold flex items-center mt-0.5">
                          <span className="material-symbols-outlined text-[14px] mr-1">flag</span>
                          Target: ₺{product.target_price.toLocaleString()}
                        </p>
                      )}
                    </div>
                  </div>
                  <button 
                    onClick={() => handleOpenDetail(product)}
                    className="w-full py-2.5 mt-auto rounded-lg bg-primary hover:bg-primary/90 text-white text-sm font-semibold transition-all duration-300 hover:shadow-lg hover:shadow-primary/30 active:scale-[0.98] flex items-center justify-center gap-2 overflow-hidden relative after:absolute after:inset-0 after:bg-white/20 after:-translate-x-full hover:after:translate-x-full after:transition-transform after:duration-500"
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* Modals */}
      <AddProductModal 
        isOpen={isAddModalOpen} 
        onClose={() => setIsAddModalOpen(false)} 
        onProductAdded={fetchProducts}
      />
      <ProductDetailModal 
        isOpen={isDetailModalOpen} 
        onClose={() => setIsDetailModalOpen(false)}
        product={selectedProduct}
        onProductDeleted={fetchProducts}
      />
    </main>
  );
};

export default WishlistDashboard;
