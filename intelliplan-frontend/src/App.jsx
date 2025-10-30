import React, { useState, useEffect } from 'react';
import { Loader, AlertCircle } from 'lucide-react';
import apiService from './services/api';
import TimetableGrid from './components/TimetableGrid';
import ConstraintInput from './components/ConstraintInput';
import ExportModal from './components/ExportModal';
import CourseSelectionModal from './components/CourseSelectionModal';

function App() {
  const [selectedCourses, setSelectedCourses] = useState([]);
  const [selectedSlots, setSelectedSlots] = useState({});
  const [timetables, setTimetables] = useState([]);
  const [currentTimetableIndex, setCurrentTimetableIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showExportModal, setShowExportModal] = useState(false);
  const [showCourseModal, setShowCourseModal] = useState(false);
  const [systemStats, setSystemStats] = useState(null);
  const [appliedConstraints, setAppliedConstraints] = useState([]);

  // Load system info on mount
  useEffect(() => {
    loadSystemStats();
  }, []);

  const loadSystemStats = async () => {
    try {
      const response = await apiService.getStats();
      setSystemStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleGenerateTimetables = async () => {
    if (selectedCourses.length === 0) {
      setError('Please select at least one course');
      return;
    }

    try {
      setError('');
      setLoading(true);
      setAppliedConstraints([]);
      const response = await apiService.generateTimetables(selectedCourses, selectedSlots);
      
      const generated = response.data.timetables || [];
      if (generated.length === 0) {
        setError('No valid timetable combinations found. Try selecting different courses.');
      } else {
        setTimetables(generated);
        setCurrentTimetableIndex(0);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Error generating timetables');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterApplied = (filtered, constraints) => {
    if (filtered.length === 0 && constraints.length > 0) {
      // Only show error if filters were applied but no results found
      setError('No timetables match the applied constraint');
    } else {
      setTimetables(filtered);
      setCurrentTimetableIndex(0);
      setAppliedConstraints(constraints);
      setError('');
    }
  };

  const handleExport = () => {
    if (timetables.length > 0) {
      setShowExportModal(true);
    }
  };

  const currentTimetable = timetables[currentTimetableIndex];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-4">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-lg mb-4">
        <div className="px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-white">📚 IntelliPlan</h1>
              <p className="text-blue-100 text-sm">AI-Powered Course Scheduler</p>
            </div>
            {systemStats && (
              <div className="text-right text-sm text-blue-100">
                <p>📊 Courses: <span className="font-bold text-white">{systemStats.total_courses}</span> | Slots: <span className="font-bold text-white">{systemStats.total_slots}</span></p>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Error Alert */}
      {error && (
        <div className="mb-4 bg-red-900 border border-red-700 rounded-lg p-3 flex items-start gap-3 animate-pulse">
          <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={18} />
          <div>
            <h3 className="font-semibold text-red-100">⚠️ {error}</h3>
          </div>
        </div>
      )}

      {/* Top Control Bar */}
      <div className="mb-4 bg-white rounded-lg shadow-lg p-4 flex items-center justify-between flex-wrap gap-4">
        {/* Left: Course Selection Button */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowCourseModal(true)}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-2 px-6 rounded-lg transition flex items-center gap-2 text-sm shadow-md"
          >
            📚 Select Courses ({selectedCourses.length})
          </button>
        </div>

        {/* Right: Generate & Export Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleGenerateTimetables}
            disabled={loading || selectedCourses.length === 0}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-2 px-6 rounded-lg transition flex items-center gap-2 text-sm shadow-md"
          >
            {loading ? (
              <>
                <Loader size={16} className="animate-spin" />
                Generating...
              </>
            ) : (
              <>
                ✨ Generate
              </>
            )}
          </button>

          {timetables.length > 0 && (
            <button
              onClick={handleExport}
              className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded-lg transition text-sm shadow-md"
            >
              📥 Export as PDF
            </button>
          )}
        </div>
      </div>

      {/* Info Line */}
      {timetables.length > 0 && (
        <div className="mb-4 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-gray-700">
            <span className="font-bold text-blue-600">{timetables.length}</span> option(s) found • 
            <span className="font-bold text-blue-600 ml-2">Option {currentTimetableIndex + 1}/{timetables.length}</span>
          </p>
        </div>
      )}

      {/* Main Grid Layout - Timetable & Filters */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 h-[calc(100vh-300px)]">
        
        {/* CENTER PANEL - Timetable Grid (3 columns) */}
        <div className="lg:col-span-3 flex flex-col gap-4">
          {timetables.length > 0 ? (
            <>
              <div className="bg-white rounded-lg shadow-lg p-4 flex-1 overflow-auto">
                <TimetableGrid
                  timetable={currentTimetable}
                  currentIndex={currentTimetableIndex}
                  totalCount={timetables.length}
                  onPrevious={() => setCurrentTimetableIndex(Math.max(0, currentTimetableIndex - 1))}
                  onNext={() => setCurrentTimetableIndex(Math.min(timetables.length - 1, currentTimetableIndex + 1))}
                  onExport={handleExport}
                />
              </div>
            </>
          ) : (
            <div className="bg-white rounded-lg shadow-lg p-12 flex-1 flex flex-col items-center justify-center">
              <div className="text-5xl mb-3">📅</div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Ready to Schedule</h3>
              <p className="text-gray-600 text-sm text-center max-w-xs">
                Select courses and click Generate to see your timetable options
              </p>
            </div>
          )}
        </div>

        {/* RIGHT PANEL - NLP Filter (1 column) */}
        <div className="lg:col-span-1 flex flex-col gap-4">
          <div className="bg-white rounded-lg shadow-lg p-4 flex-1 overflow-y-auto">
            <h2 className="font-bold text-lg text-gray-900 mb-3 flex items-center gap-2">
              🔍 <span>Filters</span>
            </h2>
            
            {timetables.length > 0 ? (
              <>
                <ConstraintInput
                  timetables={timetables}
                  onFilterApplied={handleFilterApplied}
                  onError={setError}
                  appliedConstraints={appliedConstraints}
                />
                
                {/* Applied Constraints Display */}
                {appliedConstraints.length > 0 && (
                  <div className="mt-4 pt-4 border-t">
                    <p className="text-xs font-semibold text-gray-700 mb-2">Applied Filters:</p>
                    <div className="space-y-1">
                      {appliedConstraints.map((constraint, idx) => (
                        <div key={idx} className="text-xs bg-blue-50 text-blue-900 p-2 rounded border border-blue-200">
                          ✓ {constraint}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-8">
                <p className="text-sm text-gray-600">
                  Generate timetables first, then apply filters here
                </p>
              </div>
            )}
          </div>

          {/* Quick Stats */}
          {timetables.length > 0 && (
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg shadow-lg p-4 border border-purple-200">
              <h3 className="font-bold text-sm text-gray-900 mb-2">📊 Stats</h3>
              <div className="space-y-1 text-xs text-gray-700">
                <p>• Total options: <span className="font-bold">{timetables.length}</span></p>
                <p>• Selected: <span className="font-bold">{selectedCourses.length}</span> courses</p>
                <p>• Current: <span className="font-bold">#{currentTimetableIndex + 1}</span></p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Course Selection Modal */}
      <CourseSelectionModal
        isOpen={showCourseModal}
        onClose={() => setShowCourseModal(false)}
        onConfirm={(selected, slots) => {
          setSelectedCourses(selected);
          setSelectedSlots(slots || {});
          setShowCourseModal(false);
        }}
        selectedCourses={selectedCourses}
      />

      {/* Export Modal */}
      {showExportModal && (
        <ExportModal
          timetable={currentTimetable}
          onClose={() => setShowExportModal(false)}
          onConfirm={() => setShowExportModal(false)}
        />
      )}
    </div>
  );
}

export default App;
