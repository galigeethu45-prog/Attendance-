/**
 * Multi-Date Picker for Leave and WFH Requests
 * Supports both calendar selection and manual comma-separated entry
 */

function initMultiDatePicker(calendarId, manualId, hiddenId, modeSelectId, rangeFieldsId, specificFieldsId) {
    // Initialize Flatpickr with multiple date selection
    const picker = flatpickr(`#${calendarId}`, {
        mode: "multiple",
        dateFormat: "Y-m-d",
        minDate: "today",
        onChange: function(selectedDates, dateStr) {
            // Format dates to YYYY-MM-DD
            const dates = selectedDates.map(d => {
                const year = d.getFullYear();
                const month = String(d.getMonth() + 1).padStart(2, '0');
                const day = String(d.getDate()).padStart(2, '0');
                return `${year}-${month}-${day}`;
            });
            
            // Update hidden field with JSON array
            document.getElementById(hiddenId).value = JSON.stringify(dates);
            
            // Sync to manual textarea
            document.getElementById(manualId).value = dates.join(', ');
        }
    });

    // Manual entry sync to calendar
    document.getElementById(manualId).addEventListener('blur', function() {
        const manualDates = this.value.split(',').map(d => d.trim()).filter(d => d);
        
        // Validate date format
        const validDates = manualDates.filter(d => /^\d{4}-\d{2}-\d{2}$/.test(d));
        
        if (validDates.length !== manualDates.length) {
            alert('Please use YYYY-MM-DD format for all dates');
            return;
        }
        
        // Update hidden field
        document.getElementById(hiddenId).value = JSON.stringify(validDates);
        
        // Update calendar picker
        picker.setDate(validDates);
    });

    // Mode toggle handler
    document.getElementById(modeSelectId).addEventListener('change', function() {
        const rangeFields = document.getElementById(rangeFieldsId);
        const specificFields = document.getElementById(specificFieldsId);
        
        if (this.value === 'specific') {
            rangeFields.style.display = 'none';
            specificFields.style.display = 'block';
            
            // Clear range fields
            const startDate = rangeFields.querySelector('[name="start_date"]');
            const endDate = rangeFields.querySelector('[name="end_date"]');
            if (startDate) startDate.value = '';
            if (endDate) endDate.value = '';
        } else {
            rangeFields.style.display = 'block';
            specificFields.style.display = 'none';
            
            // Clear specific dates
            document.getElementById(hiddenId).value = '';
            document.getElementById(manualId).value = '';
            picker.clear();
        }
    });
}

// Helper function to format date
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}
