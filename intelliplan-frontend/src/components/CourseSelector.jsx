import React, { useState, useEffect } from 'react';
import { ChevronDown, Search, Plus } from 'lucide-react';
import apiService from '../services/api';

/**
 * CourseSelector Component
 * Allows users to browse and multi-select courses
 */
export default function CourseSelector({ onCoursesSelected, selectedCourses }) {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCourse, setExpandedCourse] = useState(null);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const response = await apiService.getCourses();
      setCourses(response.data.courses || []);
    } catch (error) {
      console.error('Error loading courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredCourses = courses.filter(course =>
    course.course_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    course.course_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCourseToggle = (courseCode) => {
    const newSelected = selectedCourses.includes(courseCode)
      ? selectedCourses.filter(c => c !== courseCode)
      : [...selectedCourses, courseCode];
    onCoursesSelected(newSelected);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-4">📚 Select Courses</h2>
        <div className="relative">
          <Search className="absolute left-3 top-3 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search by code or name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {loading && <p className="text-center text-gray-500">Loading courses...</p>}

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {filteredCourses.map(course => (
          <div
            key={course.course_code}
            className="border border-gray-200 rounded-lg hover:bg-gray-50 transition"
          >
            <div
              className="p-4 flex items-center justify-between cursor-pointer"
              onClick={() => setExpandedCourse(
                expandedCourse === course.course_code ? null : course.course_code
              )}
            >
              <div className="flex-1">
                <div className="font-semibold text-gray-900">{course.course_code}</div>
                <div className="text-sm text-gray-600">{course.course_name}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {course.available_slots} slots • {course.credits} credits
                </div>
              </div>
              <button
                className={`ml-4 p-2 hover:bg-gray-200 rounded transition ${
                  selectedCourses.includes(course.course_code) ? 'bg-blue-100' : ''
                }`}
                onClick={(e) => {
                  e.stopPropagation();
                  handleCourseToggle(course.course_code);
                }}
              >
                <Plus size={20} className={
                  selectedCourses.includes(course.course_code) ? 'text-blue-600' : 'text-gray-400'
                } />
              </button>
              <ChevronDown
                size={20}
                className={`ml-2 transition transform ${
                  expandedCourse === course.course_code ? 'rotate-180' : ''
                }`}
              />
            </div>

            {expandedCourse === course.course_code && (
              <div className="px-4 pb-4 bg-gray-50 border-t">
                <h4 className="font-semibold text-sm mb-2">Available Slots:</h4>
                <div className="space-y-2">
                  {course.slot_options.map((slot, idx) => (
                    <div key={idx} className="text-sm bg-white p-2 rounded border border-gray-200">
                      <div className="font-mono font-semibold text-gray-900">{slot.slot_number}</div>
                      <div className="text-gray-600">Faculty: {slot.faculty}</div>
                      <div className="text-gray-500 text-xs mt-1">
                        {slot.timings.map((t, i) => (
                          <div key={i}>{t.day}: {t.start} - {t.end}</div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t">
        <p className="text-sm text-gray-600">
          Selected: <span className="font-bold text-blue-600">{selectedCourses.length}</span> course(s)
        </p>
      </div>
    </div>
  );
}
