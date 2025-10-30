import React, { useState, useMemo } from 'react';
import { X, Search, Check, ChevronDown } from 'lucide-react';
import apiService from '../services/api';

/**
 * CourseSelectionModal Component
 * Beautiful modal popup for easy course selection with slot preferences
 */
export default function CourseSelectionModal({ isOpen, onClose, onConfirm, selectedCourses }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [localSelected, setLocalSelected] = useState(selectedCourses || []);
  const [showSlotModal, setShowSlotModal] = useState(false);
  const [selectedCourseForSlot, setSelectedCourseForSlot] = useState(null);
  const [selectedSlots, setSelectedSlots] = useState({});

  // Load courses when modal opens
  React.useEffect(() => {
    if (isOpen && courses.length === 0) {
      loadCoursesData();
    }
  }, [isOpen]);

  // Update local selection when selected courses prop changes
  React.useEffect(() => {
    setLocalSelected(selectedCourses || []);
  }, [selectedCourses]);

  const loadCoursesData = async () => {
    try {
      setLoading(true);
      
      // First, ensure data is loaded on backend
      try {
        await apiService.loadData();
      } catch (e) {
        console.log('Data already loaded or error:', e.message);
      }
      
      // Then fetch the courses
      const response = await apiService.getCourses();
      console.log('API Response:', response.data);
      
      // Extract courses array from response
      const coursesList = response.data.courses || response.data || [];
      console.log('Courses loaded:', coursesList.length, 'courses');
      
      setCourses(coursesList);
    } catch (error) {
      console.error('Error loading courses:', error);
      setCourses([]);
    } finally {
      setLoading(false);
    }
  };

  // Filter courses based on search
  const filteredCourses = useMemo(() => {
    // Ensure courses is always an array
    const courseList = Array.isArray(courses) ? courses : [];
    
    if (!searchTerm.trim()) return courseList;
    
    const lower = searchTerm.toLowerCase();
    return courseList.filter(course => 
      course.course_code.toLowerCase().includes(lower) ||
      course.course_name.toLowerCase().includes(lower)
    );
  }, [courses, searchTerm]);

  const toggleCourse = (courseCode) => {
    setLocalSelected(prev => 
      prev.includes(courseCode)
        ? prev.filter(c => c !== courseCode)
        : [...prev, courseCode]
    );
  };

  const handleSelectAll = () => {
    const courseList = Array.isArray(courses) ? courses : [];
    if (localSelected.length === courseList.length) {
      setLocalSelected([]);
    } else {
      setLocalSelected(courseList.map(c => c.course_code));
    }
  };

  const handleConfirm = () => {
    onConfirm(localSelected, selectedSlots);
  };

  const openSlotModal = (course) => {
    setSelectedCourseForSlot(course);
    setShowSlotModal(true);
  };

  const closeSlotModal = () => {
    setShowSlotModal(false);
    setSelectedCourseForSlot(null);
  };

  const selectSlot = (courseCode, slotNumber) => {
    setSelectedSlots(prev => {
      const currentSlots = prev[courseCode] || [];
      let updatedSlots;
      
      // Toggle slot: if already selected, remove it; otherwise add it
      if (currentSlots.includes(slotNumber)) {
        updatedSlots = currentSlots.filter(s => s !== slotNumber);
      } else {
        updatedSlots = [...currentSlots, slotNumber];
      }
      
      return {
        ...prev,
        [courseCode]: updatedSlots
      };
    });

    // Automatically check the course if slots are selected
    if (!localSelected.includes(courseCode)) {
      setLocalSelected(prev => [...prev, courseCode]);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-6 rounded-t-2xl">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">📚 Select Courses</h2>
            <button
              onClick={onClose}
              className="text-white hover:bg-white/20 p-2 rounded-lg transition"
            >
              <X size={24} />
            </button>
          </div>

          {/* Search Box */}
          <div className="relative">
            <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/70" />
            <input
              type="text"
              placeholder="Search by code or name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder:text-white/60 focus:outline-none focus:ring-2 focus:ring-white"
            />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-8 py-6">
          {loading ? (
            <div className="flex items-center justify-center h-40">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading courses...</p>
              </div>
            </div>
          ) : filteredCourses.length === 0 ? (
            <div className="flex items-center justify-center h-40">
              <p className="text-gray-500 text-lg">No courses found</p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredCourses.map(course => {
                const courseSlots = course.slots || [];
                const isSelected = localSelected.includes(course.course_code);
                const hasSelectedSlot = selectedSlots[course.course_code];
                
                return (
                  <div
                    key={course.course_code}
                    className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg transition group border border-gray-200"
                  >
                    <label className="flex items-start gap-3 flex-1 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleCourse(course.course_code)}
                        className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 flex-shrink-0 mt-0.5"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold text-gray-900 group-hover:text-blue-600 transition">
                          {course.course_code}
                        </div>
                        <div className="text-sm text-gray-600 truncate">
                          {course.course_name}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {course.credits} credits • {course.faculty_name} • {courseSlots.length} slots
                        </div>
                        {hasSelectedSlot && hasSelectedSlot.length > 0 && (
                          <div className="text-xs text-green-600 mt-1 font-medium">
                            ✓ {hasSelectedSlot.length} slot(s) selected: {hasSelectedSlot.join(', ')}
                          </div>
                        )}
                      </div>
                    </label>
                    
                    {/* Slot Selection Button */}
                    <button
                      onClick={() => openSlotModal(course)}
                      className="px-3 py-1 text-xs font-semibold bg-purple-100 hover:bg-purple-200 text-purple-900 rounded-lg transition flex-shrink-0 flex items-center gap-1"
                    >
                      <ChevronDown size={14} />
                      Slot
                    </button>
                    
                    {isSelected && (
                      <Check size={20} className="text-green-500 flex-shrink-0" />
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t bg-gray-50 px-8 py-4 rounded-b-2xl">
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm text-gray-600">
              <span className="font-semibold text-gray-900">{localSelected.length}</span> of{' '}
              <span className="font-semibold text-gray-900">{Array.isArray(courses) ? courses.length : 0}</span> courses selected
            </div>
            <button
              onClick={handleSelectAll}
              className="text-sm font-semibold text-blue-600 hover:text-blue-700 transition"
            >
              {localSelected.length === (Array.isArray(courses) ? courses.length : 0) ? 'Deselect All' : 'Select All'}
            </button>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 font-semibold transition"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              disabled={localSelected.length === 0}
              className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition"
            >
              ✓ Confirm ({localSelected.length})
            </button>
          </div>
        </div>
      </div>

      {/* Slot Selection Modal */}
      {showSlotModal && selectedCourseForSlot && (
        <SlotSelectionModal
          course={selectedCourseForSlot}
          selectedSlot={selectedSlots[selectedCourseForSlot.course_code]}
          onSelectSlot={(slotNumber) => {
            selectSlot(selectedCourseForSlot.course_code, slotNumber);
          }}
          onClose={closeSlotModal}
        />
      )}
    </div>
  );
}

/**
 * SlotSelectionModal Component
 * Modal for selecting multiple preferred course slots
 */
function SlotSelectionModal({ course, selectedSlot, onSelectSlot, onClose }) {
  const slots = course.slots || [];
  const selectedSlots = selectedSlot || [];

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-4 rounded-t-2xl">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-xl font-bold">📍 Select Slots</h3>
              <p className="text-purple-100 text-sm mt-1">{course.course_code} - {course.course_name}</p>
              <p className="text-purple-100 text-xs mt-1">Choose one or more slots to include in combinations</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white/20 p-2 rounded-lg transition"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {slots.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No slots available</p>
          ) : (
            <div className="space-y-2">
              {slots.map((slot, idx) => {
                const timeBlocks = slot.time_blocks || [];
                const isSelected = selectedSlots.includes(slot.slot_number);
                
                return (
                  <button
                    key={idx}
                    onClick={() => {
                      onSelectSlot(slot.slot_number);
                    }}
                    className={`w-full text-left p-4 rounded-lg border-2 transition ${
                      isSelected
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-200 hover:border-purple-300 hover:bg-purple-50'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-0.5 ${
                        isSelected ? 'bg-green-500 border-green-500' : 'border-gray-400'
                      }`}>
                        {isSelected && <Check size={14} className="text-white" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold text-gray-900">
                          {slot.slot_number}
                        </div>
                        <div className="text-xs text-gray-600 mt-1">
                          {timeBlocks.length} class{timeBlocks.length !== 1 ? 'es' : ''}
                        </div>
                        <div className="text-xs text-gray-500 mt-2 space-y-1">
                          {timeBlocks.map((block, bidx) => (
                            <div key={bidx} className="flex items-center gap-2">
                              <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded">
                                {block.day.slice(0, 3)} {block.start_time} - {block.end_time}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t px-6 py-3 bg-gray-50 rounded-b-2xl">
          <div className="mb-3">
            <p className="text-xs font-semibold text-gray-700 mb-2">
              Selected: {selectedSlots.length} of {slots.length} slots
            </p>
            {selectedSlots.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {selectedSlots.map((slotNum, idx) => (
                  <span key={idx} className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full font-medium">
                    {slotNum}
                  </span>
                ))}
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="w-full px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-100 rounded-lg transition"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
