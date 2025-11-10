// Usage tracking service for ParentShield.AI dashboard
class UsageTracker {
  constructor() {
    this.storageKey = 'parentshield_usage_stats';
    this.historyStorageKey = 'parentshield_usage_history';
    this.initializeStats();
  }

  initializeStats() {
    const existingStats = localStorage.getItem(this.storageKey);
    if (!existingStats) {
      const initialStats = {
        securityLessons: 0,
        transactionFraud: 0,
        messageFraud: 0,
        userFeedback: 0,
        reportGenerator: 0,
        gameFeature: 0,
        lastUpdated: new Date().toISOString()
      };
      localStorage.setItem(this.storageKey, JSON.stringify(initialStats));
    }
    
    // Initialize history storage if it doesn't exist
    const existingHistory = localStorage.getItem(this.historyStorageKey);
    if (!existingHistory) {
      const initialHistory = {
        securityLessons: [],
        transactionFraud: [],
        messageFraud: [],
        userFeedback: [],
        reportGenerator: [],
        gameFeature: [],
        lastUpdated: new Date().toISOString(),
        lastReset: new Date().toISOString()
      };
      localStorage.setItem(this.historyStorageKey, JSON.stringify(initialHistory));
    }
  }

  incrementUsage(feature) {
    // Remove the session-based restriction so counter increments every time
    // Previously: Check if we've already incremented this feature in the current session
    // const sessionKey = `parentshield_${feature}_incremented`;
    // if (sessionStorage.getItem(sessionKey)) {
    //   // Already incremented in this session, don't increment again
    //   const stats = JSON.parse(localStorage.getItem(this.storageKey));
    //   return stats[feature] || 0;
    // }
    // 
    // // Mark that we've incremented this feature in the current session
    // sessionStorage.setItem(sessionKey, 'true');
    
    const stats = JSON.parse(localStorage.getItem(this.storageKey));
    if (stats[feature] !== undefined) {
      const oldValue = JSON.stringify(stats);
      stats[feature] += 1;
      stats.lastUpdated = new Date().toISOString();
      localStorage.setItem(this.storageKey, JSON.stringify(stats));
      
      // For reportGenerator, also store historical data
      const history = JSON.parse(localStorage.getItem(this.historyStorageKey));
      const timestamp = new Date().toISOString();
      history[feature].push({
        timestamp: timestamp,
        count: stats[feature]
      });
      // Keep only the last 50 records to prevent storage bloat
      if (history[feature].length > 50) {
        history[feature] = history[feature].slice(-50);
      }
      history.lastUpdated = timestamp;
      localStorage.setItem(this.historyStorageKey, JSON.stringify(history));
      
      // Dispatch storage event to notify other tabs/components
      window.dispatchEvent(new StorageEvent('storage', {
        key: this.storageKey,
        oldValue: oldValue,
        newValue: JSON.stringify(stats)
      }));
      
      // Dispatch custom event for components that listen to it
      window.dispatchEvent(new CustomEvent('usageStatsUpdated', {
        detail: { feature, count: stats[feature] }
      }));
      
      console.log(`Incremented ${feature} usage to ${stats[feature]}`);
      return stats[feature];
    }
    return 0;
  }

  getUsageStats() {
    const stats = JSON.parse(localStorage.getItem(this.storageKey));
    return stats || {
      securityLessons: 0,
      transactionFraud: 0,
      messageFraud: 0,
      userFeedback: 0,
      reportGenerator: 0,
      gameFeature: 0,
      lastUpdated: new Date().toISOString()
    };
  }

  getHistoricalData() {
    const history = JSON.parse(localStorage.getItem(this.historyStorageKey));
    return history || {
      securityLessons: [],
      transactionFraud: [],
      messageFraud: [],
      userFeedback: [],
      reportGenerator: [],
      gameFeature: [],
      lastUpdated: null,
      lastReset: new Date().toISOString()
    };
  }

  resetStats() {
    // Remove session key clearing since we're no longer using session-based restrictions
    // Previously: Clear all session increment flags
    // Object.keys(this.getUsageStats()).forEach(key => {
    //   if (key !== 'lastReset' && key !== 'lastUpdated') {
    //     sessionStorage.removeItem(`parentshield_${key}_incremented`);
    //   }
    // });
    
    // Preserve historical data for report generator
    const history = this.getHistoricalData();
    
    const initialStats = {
      securityLessons: 0,
      transactionFraud: 0,
      messageFraud: 0,
      userFeedback: 0,
      reportGenerator: 0,
      gameFeature: 0,
      lastUpdated: new Date().toISOString()
    };
    localStorage.setItem(this.storageKey, JSON.stringify(initialStats));
    
    // Update history with reset event
    history.lastReset = new Date().toISOString();
    localStorage.setItem(this.historyStorageKey, JSON.stringify(history));
    
    // Dispatch storage event to notify other tabs/components
    window.dispatchEvent(new StorageEvent('storage', {
      key: this.storageKey,
      oldValue: JSON.stringify(initialStats),
      newValue: JSON.stringify(initialStats)
    }));
    
    // Dispatch custom event for components that listen to it
    window.dispatchEvent(new CustomEvent('usageStatsUpdated'));
    
    return initialStats;
  }
}

// Create a singleton instance
const usageTracker = new UsageTracker();

export default usageTracker;