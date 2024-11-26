$(document).ready(function() {
    $('#id_employees').select2({
        placeholder: "Выберите сотрудников",
        allowClear: true,
        width: '100%',
        // Включение поиска по сотрудникам
        minimumInputLength: 1,  // Начать поиск при вводе хотя бы 1 символа
    });
});