document.getElementById('toggleSwitch').addEventListener('change', function() {
    if (this.checked) {
        document.getElementById('startTestForm').submit();
    } else {
        document.getElementById('stopTestForm').submit();
    }
});