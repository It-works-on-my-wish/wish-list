import React from 'react';

const Layout = ({ children }) => {
  return (
    <div className="flex h-auto min-h-screen w-full flex-col overflow-x-hidden">
      <header className="flex items-center justify-between whitespace-nowrap border-b border-slate-200 dark:border-slate-800 px-6 py-4 lg:px-10 lg:py-4 sticky top-0 bg-background-light/90 dark:bg-background-dark/90 backdrop-blur-md z-10 transition-colors duration-300">
        <div className="flex items-center gap-6 lg:gap-8">
          <div className="flex items-center gap-3 text-slate-900 dark:text-white">
            <div className="text-primary material-symbols-outlined text-2xl group-hover:scale-110 transition-transform duration-300">
              shopping_bag
            </div>
            <h2 className="text-lg font-bold leading-tight tracking-tight hidden sm:block">Wishlist Tracker</h2>
          </div>
          <label className="flex flex-col min-w-40 sm:min-w-64 max-w-md h-10 group">
            <div className="flex w-full flex-1 items-stretch rounded-full h-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 overflow-hidden shadow-sm group-focus-within:ring-2 group-focus-within:ring-primary/50 transition-all duration-300">
              <div className="text-slate-400 dark:text-slate-500 flex items-center justify-center pl-4 pr-2">
                <span className="material-symbols-outlined text-[20px]">search</span>
              </div>
              <input 
                className="form-input flex w-full min-w-0 flex-1 resize-none bg-transparent text-slate-900 dark:text-white focus:outline-none focus:ring-0 border-none h-full placeholder:text-slate-400 dark:placeholder:text-slate-500 px-2 text-sm font-medium leading-normal" 
                placeholder="Search products..." 
              />
            </div>
          </label>
        </div>
        
        <div className="flex items-center gap-6 lg:gap-8">
          <nav className="hidden md:flex items-center gap-6">
            <a className="text-primary text-sm font-semibold leading-normal border-b-2 border-primary pb-1 transition-all duration-300 hover:text-primary/80" href="#">Dashboard</a>
            <a className="text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all duration-300 text-sm font-medium leading-normal pb-1 hover:border-b-2 hover:border-slate-300 dark:hover:border-slate-600" href="#">My Lists</a>
            <a className="text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all duration-300 text-sm font-medium leading-normal pb-1 hover:border-b-2 hover:border-slate-300 dark:hover:border-slate-600" href="#">Price Drops</a>
            <a className="text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all duration-300 text-sm font-medium leading-normal pb-1 hover:border-b-2 hover:border-slate-300 dark:hover:border-slate-600" href="#">Settings</a>
          </nav>
          
          <div className="flex items-center gap-4">
            <button className="text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors duration-300 rounded-full p-2 hover:bg-slate-100 dark:hover:bg-slate-800 relative hover:scale-110 active:scale-95">
              <span className="material-symbols-outlined">notifications</span>
              <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-background-light dark:border-background-dark animate-pulse"></span>
            </button>
            <div 
              className="bg-center bg-no-repeat aspect-square bg-cover rounded-full h-9 w-9 border border-slate-200 dark:border-slate-700 cursor-pointer hover:ring-2 hover:ring-primary/50 transition-all duration-300 shadow-sm hover:shadow-md" 
              style={{ backgroundImage: 'url("https://ui-avatars.com/api/?name=User&background=137fec&color=fff")' }}
            ></div>
          </div>
        </div>
      </header>
      
      {children}
    </div>
  );
};

export default Layout;
