import React, { useState, useEffect} from 'react';
import { deleteProduct, updateProduct,getProductPriceHistory } from '../api';

const ProductDetailModal = ({ isOpen, onClose, product, onProductDeleted }) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isPurchasing, setIsPurchasing] = useState(false);
  const [priceHistory, setPriceHistory] = useState([]);
  useEffect(() => {
    if (isOpen && product) {
      getProductPriceHistory(product.id)
        .then(data => setPriceHistory(data || []))
        .catch(err => console.error("Failed to load price history", err));
    }
  }, [isOpen, product]);

  if (!isOpen || !product) return null;

  const isPurchased = product.purchase_state === 'purchased';

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

  const handleMarkPurchased = async () => {
    setIsPurchasing(true);
    try {
      await updateProduct(product.id, { purchase_state: "purchased" });
      if (onProductDeleted) onProductDeleted();
      onClose();
    } catch (error) {
      console.error("Failed to mark as purchased:", error);
      alert("Failed to update product status");
    } finally {
      setIsPurchasing(false);
    }
  };

  const handleMarkPending = async () => {
    setIsPurchasing(true);
    try {
      await updateProduct(product.id, { purchase_state: "pending" });
      if (onProductDeleted) onProductDeleted();
      onClose();
    } catch (error) {
      console.error("Failed to mark as pending:", error);
      alert("Failed to update product status");
    } finally {
      setIsPurchasing(false);
    }
  };

 

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm z-0" onClick={onClose}></div>
      <div className="relative z-10 bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-5xl h-[90vh] md:h-[80vh] min-h-[600px] flex flex-col overflow-hidden border border-slate-200 dark:border-slate-700 animate-slide-up">

        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold">Product Details</h2>
            <span className={`px-2.5 py-1 rounded-full text-xs font-bold flex items-center gap-1 ${isPurchased ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' : 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400'}`}>
              <span className="material-symbols-outlined text-[14px]">{isPurchased ? 'check_circle' : 'schedule'}</span>
              {isPurchased ? 'Purchased' : 'Pending'}
            </span>
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 transition-colors rounded-full p-1 hover:bg-slate-100 dark:hover:bg-slate-700 active:scale-95">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 p-6 overflow-y-auto w-full">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Left Column: Product Image & Info */}
            <div className="w-full lg:w-1/3 flex flex-col gap-6">
              <div
                className="w-full aspect-square rounded-xl bg-slate-100 dark:bg-slate-900 bg-center bg-no-repeat bg-contain border border-slate-200 dark:border-slate-700 hover:scale-[1.02] transition-transform duration-300"
                style={{ backgroundImage: `url("${product.image_url || 'https://placehold.co/400x400?text=No+Image'}")` }}
              ></div>
              <div>
                <h3 className="text-2xl font-bold mb-2 break-words leading-tight line-clamp-3" title={product.name}>{product.name}</h3>
                <p className="text-slate-600 dark:text-slate-400 text-sm capitalize">{product.priority} Priority</p>
              </div>
              <div className="flex flex-col gap-4 bg-slate-50 dark:bg-[#151f2b] p-4 rounded-lg border border-slate-200 dark:border-slate-700 transition-colors hover:border-slate-300 dark:hover:border-slate-600">
                <div className="flex justify-between items-center group">
                  <span className="text-slate-500 dark:text-slate-400 text-sm group-hover:text-primary transition-colors">Status</span>
                  <span className={`font-medium px-2 py-1 rounded text-xs ${isPurchased ? 'text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-400/10' : 'text-amber-600 dark:text-amber-400 bg-amber-100 dark:bg-amber-400/10'}`}>
                    {isPurchased ? 'Purchased' : 'Pending'}
                  </span>
                </div>
                <div className="flex justify-between items-center group">
                  <span className="text-slate-500 dark:text-slate-400 text-sm group-hover:text-primary transition-colors">Priority</span>
                  <span className={`font-medium px-2 py-1 rounded text-xs capitalize ${product.priority === 'high' ? 'text-orange-600 dark:text-orange-400 bg-orange-100 dark:bg-orange-400/10' :
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
                  <span className="font-bold text-green-600 dark:text-green-400">{product.target_price != null ? `₺${product.target_price.toLocaleString()}` : 'Not set'}</span>
                </div>
              </div>
            </div>

            {/* Right Column: Price History */}
            <div className="w-full lg:w-2/3 flex flex-col gap-6">
              <div className="flex flex-col p-6 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-[#151f2b] h-full transition-all hover:shadow-md">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <p className="text-slate-600 dark:text-slate-400 text-sm font-medium mb-1">Current Price</p>
                    <p className="text-[32px] font-bold leading-tight">{product.current_price != null ? `₺${product.current_price.toLocaleString()}` : 'NaN'}</p>
                  </div>
                  <div className="flex flex-col items-end">
                    {product.current_price != null && (
                      <div className="flex items-center gap-1 text-slate-500 bg-slate-50 dark:bg-slate-800 px-2 py-1 rounded-md">
                        <span className="text-sm font-medium">Tracking newly started</span>
                      </div>
                    )}
                  </div>
                </div>

                <p className="text-slate-700 dark:text-slate-300 text-base font-medium mb-4">Price History (Last 3 Months)</p>

                {/* Chart Area */}
                {(() => {
                  const prices = priceHistory.map(h => h.price);
                  const allValues = product.target_price != null ? [...prices, product.target_price] : prices;
                  const chartMin = allValues.length > 0 ? Math.min(...allValues) : 0;
                  const chartMax = allValues.length > 0 ? Math.max(...allValues) : 0;
                  const chartRange = chartMax - chartMin || 1;
                  
                  const getPercentY = (val) => 100 - ((val - chartMin) / chartRange) * 80 - 10;
                  const getPercentX = (i) => prices.length > 1 ? (i / (prices.length - 1)) * 100 : 50;

                  return (
                    <div className="flex flex-col flex-1 min-h-[240px] relative">
                      {/* Y-Axis Labels */}
                      <div className="absolute left-0 top-0 bottom-8 w-16 flex flex-col justify-between text-xs text-slate-400 pr-2 items-end">
                        {allValues.length >= 1 ? (
                          <>
                            <span>₺{chartMax.toLocaleString()}</span>
                            <span>₺{chartMin.toLocaleString()}</span>
                          </>
                        ) : (
                          <>
                            <span>—</span>
                            <span>—</span>
                          </>
                        )}
                      </div>

                      {/* Chart Lines */}
                      <div className="absolute left-16 right-4 lg:right-8 top-0 bottom-8 border-l border-b border-slate-200 dark:border-slate-700">
                        <div className="absolute inset-0 flex flex-col justify-between z-0">
                          <div className="w-full border-t border-dashed border-slate-200 dark:border-slate-700/50"></div>
                          <div className="w-full border-t border-dashed border-slate-200 dark:border-slate-700/50"></div>
                          <div className="w-full border-t border-dashed border-slate-200 dark:border-slate-700/50"></div>
                        </div>

                        {/* SVG Chart Container */}
                        {priceHistory.length < 2 ? (
                          <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-sm z-10">
                            Not enough data yet
                          </div>
                        ) : (
                          <div className="absolute inset-x-0 inset-y-0 z-10 top-0 bottom-0 pointer-events-none">
                            <svg className="absolute inset-0 h-full w-full" preserveAspectRatio="none" viewBox="0 0 100 100">
                              {(() => {
                                const points = prices.map((p, i) => `${getPercentX(i)},${getPercentY(p)}`);
                                const pathD = `M${points.join(' L')}`;
                                const fillD = `M${points[0]} L${points.join(' L')} L100,100 L0,100 Z`;
                                return (
                                  <>
                                    <path d={fillD} fill="url(#chart-gradient)" opacity="0.2" />
                                    <path d={pathD} fill="none" stroke="currentColor" className="text-primary" strokeWidth="2" strokeLinejoin="round" />
                                    <defs>
                                      <linearGradient id="chart-gradient" x1="0" x2="0" y1="0" y2="1">
                                        <stop className="text-primary" offset="0%" stopColor="currentColor" stopOpacity="1" />
                                        <stop className="text-primary" offset="100%" stopColor="currentColor" stopOpacity="0" />
                                      </linearGradient>
                                    </defs>
                                  </>
                                );
                              })()}
                            </svg>

                            {/* HTML Points Overlay for no aspect-ratio distortion */}
                            {prices.map((p, i) => {
                                  const percentX = getPercentX(i);
                                  const percentY = getPercentY(p);
                                  return (
                                    <React.Fragment key={i}>
                                      {/* Vertical and Horizontal Grid Crosshairs strictly bound to chart canvas */}
                                      <div className="absolute top-0 bottom-0 border-l border-dashed border-slate-300/60 dark:border-slate-600/40 pointer-events-none z-0" style={{ left: `${percentX}%` }}></div>
                                      <div className="absolute left-0 right-0 border-t border-dashed border-slate-300/60 dark:border-slate-600/40 pointer-events-none z-0" style={{ top: `${percentY}%` }}></div>

                                      <div 
                                        className="absolute z-20"
                                        style={{ 
                                          left: `${percentX}%`, 
                                          top: `${percentY}%`, 
                                        }}
                                      >
                                        {/* The Point */}
                                        <div className="absolute w-2.5 h-2.5 bg-white dark:bg-slate-800 border-2 border-primary rounded-full shadow-sm -translate-x-1/2 -translate-y-1/2 cursor-pointer hover:scale-150 transition-transform"></div>

                                        {/* The Label */}
                                        <div className="absolute -top-9 -translate-x-1/2 whitespace-nowrap flex flex-col items-center pointer-events-none bg-white/90 dark:bg-slate-800/90 px-1.5 py-0.5 rounded shadow-sm border border-slate-200 dark:border-slate-700 backdrop-blur-sm">
                                            <span className="text-[10px] font-bold text-slate-800 dark:text-slate-200">₺{p.toLocaleString()}</span>
                                            <span className="text-[9px] text-slate-500">{new Date(priceHistory[i].checked_at).toLocaleDateString('tr-TR', {month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit'})}</span>
                                        </div>
                                      </div>
                                    </React.Fragment>
                                  );
                            })}
                          </div>
                        )}

                        {/* Target Price Line */}
                        {product.target_price != null && (
                          <div className="absolute w-full border-t-2 border-green-500/50 flex z-0" style={{ top: `${getPercentY(product.target_price)}%` }}>
                            <span className="absolute right-2 -top-5 text-xs text-green-600 dark:text-green-400 font-medium bg-slate-50/80 dark:bg-slate-800/80 px-1 backdrop-blur-sm rounded">Target: ₺{product.target_price.toLocaleString()}</span>
                          </div>
                        )}
                      </div>

                      {/* X-Axis Labels */}
                      <div className="absolute left-16 right-4 lg:right-8 bottom-0 h-8 flex justify-between items-end text-xs text-slate-400 px-1">
                        {priceHistory.length >= 2 && (
                          <>
                            <span>{new Date(priceHistory[0].checked_at).toLocaleDateString('tr-TR', {month: 'short', day: 'numeric'})}</span>
                            <span>{new Date(priceHistory[priceHistory.length-1].checked_at).toLocaleDateString('tr-TR', {month: 'short', day: 'numeric'})}</span>
                          </>
                        )}
                      </div>
                    </div>
                  );
                })()}
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
            {!isPurchased ? (
              <button
                onClick={handleMarkPurchased}
                disabled={isPurchasing}
                className="px-6 py-2.5 rounded-lg bg-green-600 hover:bg-green-700 text-white text-sm font-medium transition-all flex items-center gap-2 shadow-sm focus:ring-2 focus:ring-green-500/50 active:scale-95 hover:shadow-green-500/30 disabled:opacity-50"
              >
                <span className="material-symbols-outlined text-sm">shopping_cart</span>
                {isPurchasing ? 'Updating...' : 'Mark as Purchased'}
              </button>
            ) : (
              <button
                onClick={handleMarkPending}
                disabled={isPurchasing}
                className="px-6 py-2.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-white text-sm font-medium transition-all flex items-center gap-2 shadow-sm focus:ring-2 focus:ring-amber-400/50 active:scale-95 hover:shadow-amber-500/30 disabled:opacity-50"
              >
                <span className="material-symbols-outlined text-sm">undo</span>
                {isPurchasing ? 'Updating...' : 'Mark as Pending'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailModal;
