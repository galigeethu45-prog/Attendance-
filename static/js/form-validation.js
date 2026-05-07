/**
 * Form Validation Utilities
 * Provides client-side validation for all forms in the attendance system
 */

// Date validation utilities
const DateValidator = {
    /**
     * Check if date is in valid format (YYYY-MM-DD)
     */
    isValidFormat: function(dateString) {
        const regex = /^\d{4}-\d{2}-\d{2}$/;
        return regex.test(dateString);
    },

    /**
     * Check if date is in the future (or today)
     */
    isFutureOrToday: function(dateString) {
        const inputDate = new Date(dateString);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return inputDate >= today;
    },

    /**
     * Check if end date is after or equal to start date
     */
    isEndAfterStart: function(startDate, endDate) {
        return new Date(endDate) >= new Date(startDate);
    },

    /**
     * Parse comma-separated dates and validate each
     */
    parseAndValidateDates: function(datesString) {
        if (!datesString || datesString.trim() === '') {
            return { valid: false, error: 'Please enter at least one date' };
        }

        // Check if it's a JSON array string
        let dates;
        try {
            const parsed = JSON.parse(datesString);
            if (Array.isArray(parsed)) {
                dates = parsed;
            } else {
                // Not an array, treat as comma-separated
                dates = datesString.split(',').map(d => d.trim()).filter(d => d !== '');
            }
        } catch (e) {
            // Not JSON, treat as comma-separated
            dates = datesString.split(',').map(d => d.trim()).filter(d => d !== '');
        }
        
        if (dates.length === 0) {
            return { valid: false, error: 'Please enter at least one date' };
        }

        for (let date of dates) {
            if (!this.isValidFormat(date)) {
                return { valid: false, error: `Invalid date format: ${date}. Use YYYY-MM-DD` };
            }
            if (!this.isFutureOrToday(date)) {
                return { valid: false, error: `Date must be today or in the future: ${date}` };
            }
        }

        return { valid: true, dates: dates };
    }
};

// Form field validation
const FieldValidator = {
    /**
     * Validate required text field
     */
    validateRequired: function(value, fieldName) {
        if (!value || value.trim() === '') {
            return { valid: false, error: `${fieldName} is required` };
        }
        return { valid: true };
    },

    /**
     * Validate text length
     */
    validateLength: function(value, minLength, maxLength, fieldName) {
        const length = value ? value.trim().length : 0;
        if (minLength && length < minLength) {
            return { valid: false, error: `${fieldName} must be at least ${minLength} characters` };
        }
        if (maxLength && length > maxLength) {
            return { valid: false, error: `${fieldName} must not exceed ${maxLength} characters` };
        }
        return { valid: true };
    },

    /**
     * Validate select field
     */
    validateSelect: function(value, fieldName) {
        if (!value || value === '') {
            return { valid: false, error: `Please select ${fieldName}` };
        }
        return { valid: true };
    }
};

// Display error message
function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    // Remove existing error
    const existingError = field.parentElement.querySelector('.validation-error');
    if (existingError) {
        existingError.remove();
    }

    // Add error class to field
    field.classList.add('is-invalid');

    // Create and insert error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'validation-error text-danger small mt-1';
    errorDiv.textContent = message;
    field.parentElement.appendChild(errorDiv);
}

// Clear error message
function clearError(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    field.classList.remove('is-invalid');
    const existingError = field.parentElement.querySelector('.validation-error');
    if (existingError) {
        existingError.remove();
    }
}

// Clear all errors in form
function clearAllErrors(formElement) {
    const invalidFields = formElement.querySelectorAll('.is-invalid');
    invalidFields.forEach(field => {
        field.classList.remove('is-invalid');
    });
    const errors = formElement.querySelectorAll('.validation-error');
    errors.forEach(error => error.remove());
}

/**
 * Validate Leave Request Form
 */
function validateLeaveRequestForm(event) {
    const form = event.target;
    clearAllErrors(form);
    let isValid = true;

    // Validate leave type
    const leaveType = document.getElementById('leave_type');
    const leaveTypeValidation = FieldValidator.validateSelect(leaveType.value, 'leave type');
    if (!leaveTypeValidation.valid) {
        showError('leave_type', leaveTypeValidation.error);
        isValid = false;
    }

    // Validate dates based on selection mode
    const mode = document.getElementById('dateSelectionMode').value;
    
    if (mode === 'range') {
        // Validate date range
        const startDate = document.getElementById('start_date');
        const endDate = document.getElementById('end_date');

        if (!startDate.value) {
            showError('start_date', 'Start date is required');
            isValid = false;
        } else if (!DateValidator.isFutureOrToday(startDate.value)) {
            showError('start_date', 'Start date must be today or in the future');
            isValid = false;
        }

        if (!endDate.value) {
            showError('end_date', 'End date is required');
            isValid = false;
        } else if (startDate.value && !DateValidator.isEndAfterStart(startDate.value, endDate.value)) {
            showError('end_date', 'End date must be after or equal to start date');
            isValid = false;
        }
    } else {
        // Validate specific dates
        const selectedDates = document.getElementById('selected_dates');
        if (!selectedDates.value) {
            showError('calendar_picker', 'Please select at least one date');
            isValid = false;
        } else {
            const validation = DateValidator.parseAndValidateDates(selectedDates.value);
            if (!validation.valid) {
                showError('calendar_picker', validation.error);
                isValid = false;
            }
        }
    }

    // Validate reason
    const reason = document.getElementById('reason');
    const reasonValidation = FieldValidator.validateRequired(reason.value, 'Reason');
    if (!reasonValidation.valid) {
        showError('reason', reasonValidation.error);
        isValid = false;
    } else {
        const lengthValidation = FieldValidator.validateLength(reason.value, 10, 500, 'Reason');
        if (!lengthValidation.valid) {
            showError('reason', lengthValidation.error);
            isValid = false;
        }
    }

    if (!isValid) {
        event.preventDefault();
        // Scroll to first error
        const firstError = form.querySelector('.is-invalid');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    return isValid;
}

/**
 * Validate WFH Request Form
 */
function validateWFHRequestForm(event) {
    const form = event.target;
    clearAllErrors(form);
    let isValid = true;

    // Validate dates based on selection mode
    const mode = document.getElementById('dateSelectionModeWFH').value;
    
    if (mode === 'range') {
        // Validate date range
        const startDate = document.getElementById('start_date');
        const endDate = document.getElementById('end_date');

        if (!startDate.value) {
            showError('start_date', 'Start date is required');
            isValid = false;
        } else if (!DateValidator.isFutureOrToday(startDate.value)) {
            showError('start_date', 'Start date must be today or in the future');
            isValid = false;
        }

        if (!endDate.value) {
            showError('end_date', 'End date is required');
            isValid = false;
        } else if (startDate.value && !DateValidator.isEndAfterStart(startDate.value, endDate.value)) {
            showError('end_date', 'End date must be after or equal to start date');
            isValid = false;
        }
    } else {
        // Validate specific dates
        const selectedDates = document.getElementById('selected_dates_wfh');
        if (!selectedDates.value) {
            showError('calendar_picker_wfh', 'Please select at least one date');
            isValid = false;
        } else {
            const validation = DateValidator.parseAndValidateDates(selectedDates.value);
            if (!validation.valid) {
                showError('calendar_picker_wfh', validation.error);
                isValid = false;
            }
        }
    }

    // Validate reason
    const reason = document.getElementById('reason');
    const reasonValidation = FieldValidator.validateRequired(reason.value, 'Reason');
    if (!reasonValidation.valid) {
        showError('reason', reasonValidation.error);
        isValid = false;
    } else {
        const lengthValidation = FieldValidator.validateLength(reason.value, 10, 500, 'Reason');
        if (!lengthValidation.valid) {
            showError('reason', lengthValidation.error);
            isValid = false;
        }
    }

    if (!isValid) {
        event.preventDefault();
        // Scroll to first error
        const firstError = form.querySelector('.is-invalid');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    return isValid;
}

/**
 * Validate Onsite Request Form
 */
function validateOnsiteRequestForm(event) {
    const form = event.target;
    clearAllErrors(form);
    let isValid = true;

    // Validate visit type
    const visitType = document.getElementById('visit_type');
    const visitTypeValidation = FieldValidator.validateSelect(visitType.value, 'visit type');
    if (!visitTypeValidation.valid) {
        showError('visit_type', visitTypeValidation.error);
        isValid = false;
    }

    // Validate visit date
    const visitDate = document.getElementById('visit_date');
    if (!visitDate.value) {
        showError('visit_date', 'Visit date is required');
        isValid = false;
    } else if (!DateValidator.isFutureOrToday(visitDate.value)) {
        showError('visit_date', 'Visit date must be today or in the future');
        isValid = false;
    }

    // Validate client name
    const clientName = document.getElementById('client_name');
    const clientValidation = FieldValidator.validateRequired(clientName.value, 'Client/Project name');
    if (!clientValidation.valid) {
        showError('client_name', clientValidation.error);
        isValid = false;
    } else {
        const lengthValidation = FieldValidator.validateLength(clientName.value, 2, 100, 'Client/Project name');
        if (!lengthValidation.valid) {
            showError('client_name', lengthValidation.error);
            isValid = false;
        }
    }

    // Validate location
    const location = document.getElementById('location');
    const locationValidation = FieldValidator.validateRequired(location.value, 'Location');
    if (!locationValidation.valid) {
        showError('location', locationValidation.error);
        isValid = false;
    } else {
        const lengthValidation = FieldValidator.validateLength(location.value, 2, 200, 'Location');
        if (!lengthValidation.valid) {
            showError('location', lengthValidation.error);
            isValid = false;
        }
    }

    // Validate purpose
    const purpose = document.getElementById('purpose');
    const purposeValidation = FieldValidator.validateRequired(purpose.value, 'Purpose');
    if (!purposeValidation.valid) {
        showError('purpose', purposeValidation.error);
        isValid = false;
    } else {
        const lengthValidation = FieldValidator.validateLength(purpose.value, 10, 500, 'Purpose');
        if (!lengthValidation.valid) {
            showError('purpose', lengthValidation.error);
            isValid = false;
        }
    }

    // Validate expected duration
    const duration = document.getElementById('expected_duration');
    const durationValidation = FieldValidator.validateRequired(duration.value, 'Expected duration');
    if (!durationValidation.valid) {
        showError('expected_duration', durationValidation.error);
        isValid = false;
    }

    if (!isValid) {
        event.preventDefault();
        // Scroll to first error
        const firstError = form.querySelector('.is-invalid');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    return isValid;
}

// Real-time validation on blur
function setupRealtimeValidation() {
    // Add blur event listeners to all form fields
    document.querySelectorAll('input[required], select[required], textarea[required]').forEach(field => {
        field.addEventListener('blur', function() {
            if (this.value && this.value.trim() !== '') {
                clearError(this.id);
            }
        });
    });

    // Date fields real-time validation
    const startDateFields = document.querySelectorAll('input[type="date"]');
    startDateFields.forEach(field => {
        field.addEventListener('change', function() {
            if (this.value && !DateValidator.isFutureOrToday(this.value)) {
                showError(this.id, 'Date must be today or in the future');
            } else {
                clearError(this.id);
            }
        });
    });
}

// Initialize validation on page load
document.addEventListener('DOMContentLoaded', function() {
    setupRealtimeValidation();
});
