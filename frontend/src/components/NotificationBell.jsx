import React, { useState, useEffect, useRef } from 'react';
import { getUserNotifications, markNotificationRead, markAllNotificationsRead } from '../api';

const NotificationBell = () => {
  const [notifications, setNotifications] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  const TEST_USER_ID = "123e4567-e89b-12d3-a456-426614174000";

  const fetchNotifications = async () => {
    try {
      const data = await getUserNotifications(TEST_USER_ID);
      setNotifications(data || []);
    } catch (err) {
      console.error("Failed to load notifications", err);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchNotifications();

    // Setup polling every 5 seconds for snappier real-time feeling
    const interval = setInterval(() => {
      fetchNotifications();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Close dropdown if clicked outside
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [dropdownRef]);

  const handleMarkAsRead = async (id, e) => {
    e.stopPropagation();
    try {
      await markNotificationRead(id);
      setNotifications(notifications.map(n => 
        n.id === id ? { ...n, is_read: true } : n
      ));
    } catch (err) {
      console.error("Failed to mark as read", err);
    }
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  const handleToggleOpen = () => {
    const newState = !isOpen;
    setIsOpen(newState);
    
    // Automatically mark all as seen if opening and there are unread
    if (newState && unreadCount > 0) {
      // Optimitically update UI
      setNotifications(prev => prev.map(n => ({...n, is_read: true})));
      // Run async API request in background
      markAllNotificationsRead(TEST_USER_ID).catch(err => console.error("Failed to mark all as read:", err));
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button 
        onClick={handleToggleOpen}
        className="text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors duration-300 rounded-full p-2 hover:bg-slate-100 dark:hover:bg-slate-800 relative hover:scale-110 active:scale-95"
      >
        <span className="material-symbols-outlined">notifications</span>
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 text-[9px] font-bold text-white bg-red-500 rounded-full border border-background-light dark:border-background-dark flex items-center justify-center animate-pulse">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 overflow-hidden z-50 animate-fade-in">
          <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center bg-slate-50 dark:bg-slate-900/50">
            <h3 className="font-bold text-slate-900 dark:text-white">Notifications</h3>
            {unreadCount > 0 && (
              <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full font-semibold">
                {unreadCount} new
              </span>
            )}
          </div>
          
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-slate-500 flex flex-col items-center gap-2">
                <span className="material-symbols-outlined text-4xl opacity-50">notifications_paused</span>
                <p>No notifications yet</p>
              </div>
            ) : (
              <ul className="flex flex-col">
                {notifications.map((notif) => (
                  <li 
                    key={notif.id} 
                    className={`p-4 border-b border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors flex gap-3 ${!notif.is_read ? 'bg-primary/5 dark:bg-primary/10' : ''}`}
                  >
                    <div className={`mt-0.5 w-2 h-2 rounded-full shrink-0 ${!notif.is_read ? 'bg-primary' : 'bg-transparent'}`}></div>
                    <div className="flex-1 flex flex-col min-w-0">
                      <p className={`text-sm break-words whitespace-normal leading-snug ${!notif.is_read ? 'font-semibold text-slate-900 dark:text-white' : 'text-slate-600 dark:text-slate-300'}`}>
                        {notif.message}
                      </p>
                      <span className="text-xs text-slate-400 mt-1">
                        {new Date(notif.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                      </span>
                    </div>
                    {!notif.is_read && (
                      <button 
                        onClick={(e) => handleMarkAsRead(notif.id, e)}
                        className="text-primary hover:text-primary/70 shrink-0 self-start p-1 rounded hover:bg-primary/10 transition-colors"
                        title="Mark as read"
                      >
                        <span className="material-symbols-outlined text-[18px]">done</span>
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
