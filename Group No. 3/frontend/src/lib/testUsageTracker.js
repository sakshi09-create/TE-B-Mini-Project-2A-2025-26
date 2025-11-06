// Simple test for usage tracker
import usageTracker from './usageTracker';

console.log('Testing usage tracker...');

// Get initial stats
const initialStats = usageTracker.getUsageStats();
console.log('Initial stats:', initialStats);

// Increment some usage
usageTracker.incrementUsage('securityLessons');
usageTracker.incrementUsage('messageFraud');
usageTracker.incrementUsage('messageFraud');

// Check updated stats
const updatedStats = usageTracker.getUsageStats();
console.log('Updated stats:', updatedStats);

console.log('Test completed successfully!');