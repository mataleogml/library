$(document).ready(function() {
    $("#title").autocomplete({
        source: function(request, response) {
            $.getJSON("/get_titles", {
                term: request.term
            }, function(data) {
                response(data.map(function(item) {
                    return item[0] + " by " + item[1] + " | " + item[2];
                }));
            });
        },
        minLength: 2
    });
    
    $("#author").autocomplete({
        source: function(request, response) {
            $.getJSON("/get_authors", {
                term: request.term
            }, function(data) {
                response(data.map(function(item) {
                    return item[0] + " | " + item[1] + " book(s)";
                }));
            });
        },
        minLength: 2
    });
    
    $('#main_subject').change(function() {
        var main_subject = $(this).val();
        if(main_subject) {
            $.getJSON('/get_secondary_subjects/' + main_subject, function(data) {
                var options = '<option value="">Select secondary subject</option>';
                for(var i = 0; i < data.length; i++) {
                    options += '<option value="' + data[i] + '">' + data[i] + '</option>';
                }
                $('#secondary_subject').html(options);
            });
        } else {
            $('#secondary_subject').html('<option value="">Select secondary subject</option>');
        }
    });
    
    $('#addBookForm').submit(function(e) {
        e.preventDefault();
        var formData = new FormData(this);
        $.ajax({
            url: '/add_book',
            type: 'POST',
            data: formData,
            success: function(response) {
                if(response.status === 'success') {
                    alert('Book added successfully. DDC: ' + response.ddc);
                    $('#addBookForm')[0].reset();
                } else {
                    alert('Error: ' + response.message);
                }
            },
            cache: false,
            contentType: false,
            processData: false
        });
    });
    
    $('#fetchISBN').click(function() {
        var isbn = $('#isbn').val();
        $.getJSON('/fetch_book_info/' + isbn, function(data) {
            if(data.status === 'success') {
                $('#title').val(data.title);
                $('#author').val(data.author);
                $('select[name="language"]').val(data.language);
            } else {
                alert('Error: ' + data.message);
            }
        });
    });
    
    $("#search_query").autocomplete({
        source: function(request, response) {
            $.getJSON("/search_autocomplete", {
                term: request.term
            }, function(data) {
                response(data.map(function(item) {
                    return item[0] + " by " + item[1] + " | " + item[2];
                }));
            });
        },
        minLength: 2
    });
});