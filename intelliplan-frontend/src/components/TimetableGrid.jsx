import React, { useMemo } from 'react';
import { ChevronLeft, ChevronRight, Download } from 'lucide-react';

/**
 * TimetableGrid Component
 * Displays generated timetables in a grid format
 */
export default function TimetableGrid({ timetable, currentIndex, totalCount, onPrevious, onNext, onExport }) {
  const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const TIME_SLOTS = [
    '08:00', '09:00', '10:00', '11:00', '12:00', '13:00',
    '14:00', '15:00', '16:00', '17:00'
  ];

  // Build grid data structure
  const gridData = useMemo(() => {
    if (!timetable || !timetable.slots) return {};

    const grid = {};
    DAYS.forEach(day => {
      grid[day] = {};
      TIME_SLOTS.forEach(time => {
        grid[day][time] = [];
      });
    });

    timetable.slots.forEach(slot => {
      slot.time_blocks.forEach(block => {
        if (grid[block.day] && grid[block.day][block.start_time]) {
          grid[block.day][block.start_time].push(slot);
        }
      });
    });

    return grid;
  }, [timetable]);

  const handleExport = () => {
    if (onExport) {
      onExport(timetable);
    }
  };

  if (!timetable) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 text-center">
        <p className="text-gray-500">No timetable to display</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold">📅 Timetable {currentIndex + 1} of {totalCount}</h2>
          <p className="text-sm text-gray-600 mt-1">
            Total Credits: <span className="font-bold text-blue-600">{timetable.total_credits}</span>
          </p>
        </div>
        <button
          onClick={handleExport}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
        >
          <Download size={18} />
          Export as PDF
        </button>
      </div>

      {/* Timetable Grid */}
      <div className="overflow-x-auto border border-gray-300 rounded-lg">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 border-b">
            <tr>
              <th className="p-3 text-left font-semibold text-gray-900">Time</th>
              {DAYS.map(day => (
                <th key={day} className="p-3 text-center font-semibold text-gray-900 bg-blue-50">
                  {day}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {TIME_SLOTS.map(time => (
              <tr key={time} className="border-b hover:bg-gray-50">
                <td className="p-3 font-mono font-semibold text-gray-900 bg-gray-50 sticky left-0 z-10">
                  {time}
                </td>
                {DAYS.map(day => {
                  const classes = gridData[day]?.[time] || [];
                  return (
                    <td
                      key={`${day}-${time}`}
                      className="p-2 text-center border-r border-gray-200 min-h-24 align-top"
                    >
                      {classes.map((slot, idx) => (
                        <div
                          key={idx}
                          className="bg-blue-100 border border-blue-300 rounded p-2 mb-1 text-xs"
                        >
                          <div className="font-bold text-gray-900">{slot.course_code}</div>
                          <div className="text-gray-700">{slot.slot_number}</div>
                          <div className="text-gray-600 text-xs mt-1">{slot.faculty_name}</div>
                        </div>
                      ))}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Course Details */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-semibold text-gray-900 mb-3">📚 Enrolled Courses</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {timetable.slots.map((slot, idx) => (
            <div key={idx} className="bg-white border border-gray-300 rounded p-3">
              <div className="font-semibold text-gray-900">{slot.course_code}</div>
              <div className="text-sm text-gray-600">{slot.course_name}</div>
              <div className="text-sm text-gray-500 mt-1">Slot: {slot.slot_number}</div>
              <div className="text-sm text-gray-500">Faculty: {slot.faculty_name}</div>
              <div className="text-sm text-blue-600 font-semibold mt-1">{slot.credits} credits</div>
            </div>
          ))}
        </div>
      </div>

      {/* Navigation */}
      {totalCount > 1 && (
        <div className="flex justify-between items-center mt-6 pt-4 border-t">
          <button
            onClick={onPrevious}
            disabled={currentIndex === 0}
            className="flex items-center gap-2 px-4 py-2 bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed text-gray-900 rounded-lg transition"
          >
            <ChevronLeft size={18} />
            Previous
          </button>
          <span className="text-gray-600 font-semibold">
            {currentIndex + 1} / {totalCount}
          </span>
          <button
            onClick={onNext}
            disabled={currentIndex === totalCount - 1}
            className="flex items-center gap-2 px-4 py-2 bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed text-gray-900 rounded-lg transition"
          >
            Next
            <ChevronRight size={18} />
          </button>
        </div>
      )}
    </div>
  );
}
