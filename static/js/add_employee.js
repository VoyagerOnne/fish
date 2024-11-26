function updateFileName() {
    const input = document.getElementById('file-upload');
    const fileNameSpan = document.getElementById('file-name');

    if (input.files.length > 0) {
        const fileName = input.files[0].name;
        fileNameSpan.textContent = fileName;
    } else {
        fileNameSpan.textContent = 'Выберите файл';
    }
}