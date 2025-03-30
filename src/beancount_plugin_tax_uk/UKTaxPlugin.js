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
    },

    onExtensionPageLoad(ctx) {
        console.log('Initializing tax view');
        const yearSelect = document.querySelector('#tax-year');
        if (yearSelect && yearSelect.value) {
            this.showYear(yearSelect.value);
        }
        window.showYear = this.showYear;
    }
};

export default UKTaxPlugin; 