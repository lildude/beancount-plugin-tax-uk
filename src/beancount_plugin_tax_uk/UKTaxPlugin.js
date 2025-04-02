const UKTaxPlugin = {
    init() {
        console.log("initialising UKTaxPlugin extension");
    },

    showYear(year) {
        // Hide all year sections
        document.querySelectorAll('.year-section').forEach(section => {
            section.style.display = 'none';
        });
        
        // Show selected year section
        const selectedSection = document.getElementById('year-' + year);
        if (selectedSection) {
            selectedSection.style.display = 'block';
        }

        // Save selected year to local storage
        localStorage.setItem('selectedTaxYear', year);
    },

    onExtensionPageLoad(ctx) {
        console.log('Initializing tax view');
        const yearSelect = document.querySelector('#tax-year');
        
        // Try to load saved year from local storage
        const savedYear = localStorage.getItem('selectedTaxYear');
        
        if (yearSelect) {
            if (savedYear) {
                yearSelect.value = savedYear;
            }
            if (yearSelect.value) {
                this.showYear(yearSelect.value);
            }
        }
        window.showYear = this.showYear;
    }
};

export default UKTaxPlugin; 