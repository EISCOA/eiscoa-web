const formData = new URLSearchParams();
formData.append('empresa', 'Test');
formData.append('telefono', '123456789');
formData.append('email', 'test@test.com');
formData.append('mensaje', 'Test message');

fetch('https://formsubmit.co/ajax/soporte@eiscoa.com', {
    method: 'POST',
    headers: {
        'Accept': 'application/json'
    },
    body: formData
})
.then(res => res.text())
.then(text => console.log('Response:', text))
.catch(err => console.error('Error:', err));
