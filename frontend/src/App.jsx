import React, { useState, useEffect } from 'react';
import Layout from './components/Layout';
import WishlistDashboard from './components/WishlistDashboard';
import { listUserCategories } from './api';

function App() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Using a dummy UUID for the backend testing since auth isn't built yet
  const TEST_USER_ID = "123e4567-e89b-12d3-a456-426614174000";

  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await listUserCategories(TEST_USER_ID);
        setCategories(data);
      } catch (error) {
        console.error("Failed to fetch categories. Make sure FastAPI backend is running.", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchCategories();
  }, []);

  return (
    <Layout searchQuery={searchQuery} setSearchQuery={setSearchQuery}>
      <WishlistDashboard searchQuery={searchQuery} />
    </Layout>
  );
}

export default App;
