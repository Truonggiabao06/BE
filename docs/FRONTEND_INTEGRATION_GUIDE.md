# 🚀 Frontend Integration Guide

## 📋 Overview

Hướng dẫn tích hợp frontend với **Jewelry Auction System API** cho React, Vue.js, và vanilla JavaScript.

---

## 🔧 Setup & Configuration

### 1. Environment Variables
```javascript
// .env
REACT_APP_API_BASE_URL=http://127.0.0.1:5000
REACT_APP_WS_URL=ws://127.0.0.1:5000
REACT_APP_APP_NAME=Jewelry Auction
```

### 2. API Client Setup (Axios)
```javascript
// api/client.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error.response?.data || error);
  }
);

export default apiClient;
```

---

## 🔐 Authentication Integration

### 1. Auth Service
```javascript
// services/authService.js
import apiClient from '../api/client';

class AuthService {
  async register(userData) {
    const response = await apiClient.post('/api/auth/register', userData);
    return response;
  }

  async login(email, password) {
    const response = await apiClient.post('/api/auth/login', {
      email,
      password,
    });
    
    if (response.success) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return response;
  }

  async verifyEmail(email, code) {
    return await apiClient.post('/api/auth/verify-email', {
      email,
      verification_code: code,
    });
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }

  getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }

  isEmailVerified() {
    const user = this.getCurrentUser();
    return user?.is_email_verified || false;
  }
}

export default new AuthService();
```

### 2. React Auth Hook
```javascript
// hooks/useAuth.js
import { useState, useEffect, createContext, useContext } from 'react';
import authService from '../services/authService';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    setUser(currentUser);
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const response = await authService.login(email, password);
    if (response.success) {
      setUser(response.data.user);
    }
    return response;
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    loading,
    isAuthenticated: authService.isAuthenticated(),
    isEmailVerified: authService.isEmailVerified(),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

---

## 🏺 Auction Items Integration

### 1. Auction Items Service
```javascript
// services/auctionItemsService.js
import apiClient from '../api/client';

class AuctionItemsService {
  async getItems(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await apiClient.get(`/api/auction-items?${queryString}`);
  }

  async getItem(id) {
    return await apiClient.get(`/api/auction-items/${id}`);
  }

  async createItem(itemData) {
    return await apiClient.post('/api/auction-items', itemData);
  }

  async getCategories() {
    return await apiClient.get('/api/auction-items/categories');
  }

  async searchItems(query) {
    return await apiClient.get(`/api/auction-items/search?q=${encodeURIComponent(query)}`);
  }

  async getMyItems(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await apiClient.get(`/api/auction-items/my-items?${queryString}`);
  }
}

export default new AuctionItemsService();
```

### 2. React Component Example
```javascript
// components/AuctionItemsList.jsx
import React, { useState, useEffect } from 'react';
import auctionItemsService from '../services/auctionItemsService';

const AuctionItemsList = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({});
  const [filters, setFilters] = useState({
    page: 1,
    limit: 20,
    category: '',
    status: 'active',
  });

  useEffect(() => {
    loadItems();
  }, [filters]);

  const loadItems = async () => {
    try {
      setLoading(true);
      const response = await auctionItemsService.getItems(filters);
      
      if (response.success) {
        setItems(response.data);
        setPagination(response.pagination);
      }
    } catch (error) {
      console.error('Load items error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    setFilters(prev => ({ ...prev, page: newPage }));
  };

  const handleCategoryChange = (category) => {
    setFilters(prev => ({ ...prev, category, page: 1 }));
  };

  if (loading) return <div>Đang tải...</div>;

  return (
    <div className="auction-items-list">
      <div className="filters">
        <select 
          value={filters.category} 
          onChange={(e) => handleCategoryChange(e.target.value)}
        >
          <option value="">Tất cả danh mục</option>
          <option value="ring">Nhẫn</option>
          <option value="necklace">Dây chuyền</option>
          <option value="earrings">Bông tai</option>
        </select>
      </div>

      <div className="items-grid">
        {items.map(item => (
          <div key={item.id} className="item-card">
            <img src={item.images[0]} alt={item.title} />
            <h3>{item.title}</h3>
            <p>Giá hiện tại: {item.current_price.toLocaleString()} VND</p>
            <span className={`status ${item.status}`}>
              {item.status === 'active' ? 'Đang đấu giá' : 'Đã kết thúc'}
            </span>
          </div>
        ))}
      </div>

      <div className="pagination">
        <button 
          disabled={!pagination.has_prev}
          onClick={() => handlePageChange(pagination.page - 1)}
        >
          Trước
        </button>
        <span>Trang {pagination.page} / {pagination.pages}</span>
        <button 
          disabled={!pagination.has_next}
          onClick={() => handlePageChange(pagination.page + 1)}
        >
          Sau
        </button>
      </div>
    </div>
  );
};

export default AuctionItemsList;
```

---

## 🎯 Auction Sessions Integration

### 1. Auction Sessions Service
```javascript
// services/auctionSessionsService.js
import apiClient from '../api/client';

class AuctionSessionsService {
  async getSessions(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await apiClient.get(`/api/auction-sessions?${queryString}`);
  }

  async getSession(id) {
    return await apiClient.get(`/api/auction-sessions/${id}`);
  }

  async joinSession(sessionId) {
    return await apiClient.post(`/api/auction-sessions/${sessionId}/join`);
  }

  async leaveSession(sessionId) {
    return await apiClient.post(`/api/auction-sessions/${sessionId}/leave`);
  }

  async getActiveSessions() {
    return await apiClient.get('/api/auction-sessions/active');
  }

  async getUpcomingSessions() {
    return await apiClient.get('/api/auction-sessions/upcoming');
  }
}

export default new AuctionSessionsService();
```

---

## 💰 Bidding Integration

### 1. Bid Service
```javascript
// services/bidService.js
import apiClient from '../api/client';

class BidService {
  async placeBid(sessionId, amount) {
    return await apiClient.post('/api/bids', {
      session_id: sessionId,
      amount: amount,
    });
  }

  async getSessionBids(sessionId, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await apiClient.get(`/api/bids/session/${sessionId}?${queryString}`);
  }

  async getMyBids(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await apiClient.get(`/api/bids/my-bids?${queryString}`);
  }

  async getHighestBid(sessionId) {
    return await apiClient.get(`/api/bids/session/${sessionId}/highest`);
  }
}

export default new BidService();
```

### 2. Bidding Component
```javascript
// components/BiddingPanel.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import bidService from '../services/bidService';

const BiddingPanel = ({ sessionId, minBidIncrement }) => {
  const { user, isAuthenticated, isEmailVerified } = useAuth();
  const [bidAmount, setBidAmount] = useState('');
  const [highestBid, setHighestBid] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadHighestBid();
  }, [sessionId]);

  const loadHighestBid = async () => {
    try {
      const response = await bidService.getHighestBid(sessionId);
      if (response.success) {
        setHighestBid(response.data);
      }
    } catch (error) {
      console.error('Load highest bid error:', error);
    }
  };

  const handlePlaceBid = async (e) => {
    e.preventDefault();
    
    if (!isAuthenticated) {
      alert('Vui lòng đăng nhập để đặt giá');
      return;
    }

    if (!isEmailVerified) {
      alert('Vui lòng xác thực email trước khi đặt giá');
      return;
    }

    const amount = parseFloat(bidAmount);
    if (!amount || amount <= 0) {
      alert('Vui lòng nhập số tiền hợp lệ');
      return;
    }

    try {
      setLoading(true);
      const response = await bidService.placeBid(sessionId, amount);
      
      if (response.success) {
        alert(response.message);
        setBidAmount('');
        loadHighestBid(); // Refresh highest bid
      }
    } catch (error) {
      alert(error.message || 'Có lỗi xảy ra khi đặt giá');
    } finally {
      setLoading(false);
    }
  };

  const nextMinimumBid = highestBid?.next_minimum_bid || minBidIncrement;

  return (
    <div className="bidding-panel">
      <div className="current-bid">
        <h3>Giá hiện tại</h3>
        <p className="amount">
          {highestBid?.current_price?.toLocaleString() || '0'} VND
        </p>
      </div>

      <form onSubmit={handlePlaceBid} className="bid-form">
        <div className="input-group">
          <label>Số tiền đặt giá (VND)</label>
          <input
            type="number"
            value={bidAmount}
            onChange={(e) => setBidAmount(e.target.value)}
            min={nextMinimumBid}
            step={minBidIncrement}
            placeholder={`Tối thiểu: ${nextMinimumBid.toLocaleString()}`}
            disabled={loading}
          />
        </div>
        
        <button 
          type="submit" 
          disabled={loading || !isAuthenticated || !isEmailVerified}
          className="bid-button"
        >
          {loading ? 'Đang đặt giá...' : 'Đặt giá'}
        </button>
      </form>

      {!isAuthenticated && (
        <p className="auth-notice">Vui lòng đăng nhập để tham gia đấu giá</p>
      )}
      
      {isAuthenticated && !isEmailVerified && (
        <p className="verification-notice">Vui lòng xác thực email để đặt giá</p>
      )}
    </div>
  );
};

export default BiddingPanel;
```

---

## 🔄 WebSocket Integration

### 1. WebSocket Hook
```javascript
// hooks/useWebSocket.js
import { useEffect, useRef, useState } from 'react';
import io from 'socket.io-client';

export const useWebSocket = (url) => {
  const socketRef = useRef(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    socketRef.current = io(url);

    socketRef.current.on('connect', () => {
      setConnected(true);
      console.log('WebSocket connected');
    });

    socketRef.current.on('disconnect', () => {
      setConnected(false);
      console.log('WebSocket disconnected');
    });

    return () => {
      socketRef.current.disconnect();
    };
  }, [url]);

  const emit = (event, data) => {
    if (socketRef.current) {
      socketRef.current.emit(event, data);
    }
  };

  const on = (event, callback) => {
    if (socketRef.current) {
      socketRef.current.on(event, callback);
    }
  };

  const off = (event, callback) => {
    if (socketRef.current) {
      socketRef.current.off(event, callback);
    }
  };

  return { connected, emit, on, off };
};
```

### 2. Real-time Auction Component
```javascript
// components/RealTimeAuction.jsx
import React, { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

const RealTimeAuction = ({ sessionId }) => {
  const { connected, on, off } = useWebSocket(process.env.REACT_APP_WS_URL);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    if (connected) {
      // Join auction room
      on('join_auction', { session_id: sessionId });

      // Listen for bid updates
      on('bid_placed', (data) => {
        setNotifications(prev => [...prev, {
          id: Date.now(),
          type: 'bid',
          message: `Có lượt đặt giá mới: ${data.amount.toLocaleString()} VND`,
          timestamp: new Date(),
        }]);
      });

      // Listen for auction events
      on('auction_ending', (data) => {
        setNotifications(prev => [...prev, {
          id: Date.now(),
          type: 'warning',
          message: `Phiên đấu giá sẽ kết thúc trong ${data.minutes_remaining} phút!`,
          timestamp: new Date(),
        }]);
      });

      on('auction_ended', (data) => {
        setNotifications(prev => [...prev, {
          id: Date.now(),
          type: 'info',
          message: `Phiên đấu giá đã kết thúc. Giá thắng: ${data.final_price?.toLocaleString()} VND`,
          timestamp: new Date(),
        }]);
      });
    }

    return () => {
      off('bid_placed');
      off('auction_ending');
      off('auction_ended');
    };
  }, [connected, sessionId, on, off]);

  return (
    <div className="real-time-auction">
      <div className="connection-status">
        <span className={`status ${connected ? 'connected' : 'disconnected'}`}>
          {connected ? '🟢 Kết nối' : '🔴 Mất kết nối'}
        </span>
      </div>

      <div className="notifications">
        {notifications.slice(-5).map(notification => (
          <div key={notification.id} className={`notification ${notification.type}`}>
            <span className="message">{notification.message}</span>
            <span className="time">
              {notification.timestamp.toLocaleTimeString()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RealTimeAuction;
```

---

## 💳 Payment Integration

### 1. Payment Service
```javascript
// services/paymentService.js
import apiClient from '../api/client';

class PaymentService {
  async getPaymentMethods() {
    return await apiClient.get('/api/payments/methods');
  }

  async calculateFees(amount) {
    return await apiClient.post('/api/payments/calculate-fees', { amount });
  }

  async getMyPayments(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await apiClient.get(`/api/payments/my-payments?${queryString}`);
  }
}

export default new PaymentService();
```

---

## 🎨 UI Components Examples

### 1. Loading Component
```javascript
// components/Loading.jsx
const Loading = ({ message = 'Đang tải...' }) => (
  <div className="loading">
    <div className="spinner"></div>
    <p>{message}</p>
  </div>
);
```

### 2. Error Boundary
```javascript
// components/ErrorBoundary.jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Có lỗi xảy ra</h2>
          <p>Vui lòng tải lại trang hoặc liên hệ hỗ trợ.</p>
          <button onClick={() => window.location.reload()}>
            Tải lại trang
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

---

## 🧪 Testing Examples

### 1. API Service Tests
```javascript
// __tests__/authService.test.js
import authService from '../services/authService';

describe('AuthService', () => {
  test('should login successfully', async () => {
    const mockResponse = {
      success: true,
      data: {
        access_token: 'mock-token',
        user: { id: 1, email: 'test@example.com' }
      }
    };

    // Mock API call
    jest.spyOn(authService, 'login').mockResolvedValue(mockResponse);

    const result = await authService.login('test@example.com', 'password');
    expect(result.success).toBe(true);
    expect(result.data.access_token).toBe('mock-token');
  });
});
```

---

## 📱 Mobile Considerations

### 1. Responsive Design
```css
/* Mobile-first approach */
.auction-items-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .auction-items-list {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .auction-items-list {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### 2. Touch-friendly Bidding
```javascript
// Touch-friendly bid buttons
const QuickBidButtons = ({ currentBid, minIncrement, onBid }) => {
  const quickBids = [
    currentBid + minIncrement,
    currentBid + minIncrement * 2,
    currentBid + minIncrement * 5,
  ];

  return (
    <div className="quick-bid-buttons">
      {quickBids.map(amount => (
        <button
          key={amount}
          onClick={() => onBid(amount)}
          className="quick-bid-btn"
        >
          {amount.toLocaleString()} VND
        </button>
      ))}
    </div>
  );
};
```

---

## 🔧 Best Practices

### 1. Error Handling
- Luôn handle API errors gracefully
- Hiển thị error messages bằng tiếng Việt
- Implement retry logic cho network errors

### 2. Performance
- Implement lazy loading cho images
- Use pagination cho large lists
- Cache API responses khi có thể

### 3. Security
- Không store sensitive data trong localStorage
- Validate user input trước khi gửi API
- Implement proper CORS handling

### 4. User Experience
- Hiển thị loading states
- Implement optimistic updates cho bidding
- Provide clear feedback cho user actions

---

## 📞 Support

Nếu có vấn đề trong quá trình tích hợp:
- **Email**: dev-support@jewelry-auction.com
- **Documentation**: https://docs.jewelry-auction.com
- **GitHub Issues**: https://github.com/jewelry-auction/api/issues
