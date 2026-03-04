document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.querySelector('form');
    const fileInput = document.querySelector('input[type="file"]');

    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const filePath = fileInput.value;
            // Check if file is CSV or XLSX
            const allowedExtensions = /(\.csv|\.xlsx|\.xls)$/i;
            
            if (!allowedExtensions.exec(filePath)) {
                alert('Thavaraana file! Please upload .csv or .xlsx file only.');
                fileInput.value = '';
                e.preventDefault();
                return false;
            }
        });
    }
});

// Loading spinner function (Optional)
function showLoading() {
    const btn = document.querySelector('.btn');
    btn.innerHTML = "Processing... Please wait.";
    btn.style.backgroundColor = "#ffa500";
}
