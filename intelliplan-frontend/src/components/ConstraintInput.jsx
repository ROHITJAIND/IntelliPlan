import React, { useState } from 'react';
import { Send, Loader, X, Zap } from 'lucide-react';
import apiService from '../services/api';

/**
 * NLPConstraintInput Component
 * Compact natural language constraint input optimized for side panel
 */
export default function NLPConstraintInput({ timetables, onFilterApplied, onError }) {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [appliedConstraints, setAppliedConstraints] = useState([]);
  const [originalTimetables, setOriginalTimetables] = useState(null);

  // Store original timetables when they change
  React.useEffect(() => {
    if (timetables && timetables.length > 0) {
      setOriginalTimetables(timetables);
    }
  }, [timetables]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || !originalTimetables || originalTimetables.length === 0) return;

    try {
      setLoading(true);
      // Apply filter to original timetables
      const response = await apiService.filterTimetables(originalTimetables, input);
      
      // Extract constraint text from response
      const constraintsData = response.data.constraints_applied || [];
      const constraintTexts = Array.isArray(constraintsData)
        ? constraintsData.map(c => typeof c === 'string' ? c : input)
        : [input];
      
      setAppliedConstraints([...appliedConstraints, ...constraintTexts]);
      onFilterApplied?.(response.data.filtered_timetables || [], constraintTexts);
      setInput('');
    } catch (error) {
      onError?.(error.response?.data?.detail || 'Error applying constraint');
    } finally {
      setLoading(false);
    }
  };

  const clearConstraints = () => {
    setAppliedConstraints([]);
    if (originalTimetables) {
      onFilterApplied?.(originalTimetables, []);
    }
  };

  const quickFilters = [
    { label: 'No weekends', text: 'No classes on Saturday or Sunday' },
    { label: 'Morning only', text: 'All classes before 12 PM' },
    { label: 'Afternoon start', text: 'No classes before 1 PM' },
    { label: 'No back-to-back', text: 'Avoid consecutive classes' },
  ];

  const handleQuickFilter = async (filterText) => {
    setInput(filterText);
    // Auto-submit quick filter
    try {
      setLoading(true);
      // Apply filter to original timetables
      const response = await apiService.filterTimetables(originalTimetables, filterText);
      
      // Extract constraint text from response
      const constraintsData = response.data.constraints_applied || [];
      const constraintTexts = Array.isArray(constraintsData)
        ? constraintsData.map(c => typeof c === 'string' ? c : filterText)
        : [filterText];
      
      setAppliedConstraints([...appliedConstraints, ...constraintTexts]);
      onFilterApplied?.(response.data.filtered_timetables || [], constraintTexts);
      setInput('');
    } catch (error) {
      onError?.(error.response?.data?.detail || 'Error applying constraint');
    } finally {
      setLoading(false);
    }
  };

  const removeConstraint = (index) => {
    const newConstraints = appliedConstraints.filter((_, i) => i !== index);
    setAppliedConstraints(newConstraints);
    
    if (newConstraints.length === 0) {
      // No filters left, show all original timetables
      if (originalTimetables) {
        onFilterApplied?.(originalTimetables, []);
      }
    } else {
      // Reapply remaining filters to ORIGINAL timetables
      if (originalTimetables) {
        reapplyFilters(newConstraints, originalTimetables);
      }
    }
  };

  const reapplyFilters = async (constraintsToKeep, baseTimetables) => {
    try {
      setLoading(true);
      let currentTimetables = baseTimetables;
      
      // Apply each remaining constraint sequentially to original timetables
      for (const constraint of constraintsToKeep) {
        const response = await apiService.filterTimetables(currentTimetables, constraint);
        currentTimetables = response.data.filtered_timetables || [];
        
        if (currentTimetables.length === 0) {
          break; // Stop if no results
        }
      }
      
      onFilterApplied?.(currentTimetables, constraintsToKeep);
    } catch (error) {
      onError?.(error.response?.data?.detail || 'Error reapplying filters');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      {/* Input Box */}
      <form onSubmit={handleSubmit} className="space-y-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g., No classes on weekends..."
          className="w-full p-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          rows="2"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-3 py-2 rounded-lg transition flex items-center justify-center gap-2 font-semibold text-xs"
        >
          {loading ? <Loader size={14} className="animate-spin" /> : <Send size={14} />}
          Apply Filter
        </button>
      </form>

      {/* Quick Filters */}
      {timetables.length > 0 && appliedConstraints.length === 0 && (
        <div className="space-y-1">
          <p className="text-xs font-semibold text-gray-700 px-1">Quick filters:</p>
          <div className="grid grid-cols-2 gap-1">
            {quickFilters.map((filter) => (
              <button
                key={filter.label}
                onClick={() => handleQuickFilter(filter.text)}
                disabled={loading}
                className="text-xs bg-purple-100 hover:bg-purple-200 disabled:opacity-50 text-purple-900 px-2 py-1 rounded border border-purple-300 transition font-semibold"
              >
                <Zap size={12} className="inline mr-1" />
                {filter.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Applied Constraints */}
      {appliedConstraints.length > 0 && (
        <div className="bg-blue-50 rounded-lg p-3 border border-blue-200 space-y-2">
          <div className="flex justify-between items-center">
            <p className="text-xs font-bold text-blue-900">Applied Filters ({appliedConstraints.length})</p>
            <button
              onClick={clearConstraints}
              className="text-xs text-blue-600 hover:text-blue-700 font-semibold"
            >
              Clear
            </button>
          </div>
          
          <div className="space-y-1">
            {appliedConstraints.map((constraint, idx) => (
              <div key={idx} className="bg-white border border-blue-300 rounded p-2 flex justify-between items-start gap-2">
                <div className="flex-1">
                  <p className="text-xs text-gray-700">
                    ✓ {constraint}
                  </p>
                </div>
                <button
                  onClick={() => removeConstraint(idx)}
                  className="text-red-600 hover:text-red-700 flex-shrink-0"
                >
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Examples */}
      {appliedConstraints.length === 0 && (
        <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-200 text-xs">
          <p className="font-semibold text-yellow-900 mb-2">💡 Try saying:</p>
          <ul className="space-y-1 text-yellow-800 text-xs">
            <li>• "No weekends"</li>
            <li>• "Morning classes"</li>
            <li>• "Before 1 PM"</li>
            <li>• "No back-to-back"</li>
          </ul>
        </div>
      )}
    </div>
  );
}
