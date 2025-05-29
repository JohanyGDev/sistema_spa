function abrirModal() {
    document.getElementById('modal').style.display = 'block';
    document.getElementById('overlay').style.display = 'block';
}

function cerrarModal() {
    document.getElementById('modal').style.display = 'none';
    document.getElementById('overlay').style.display = 'none';
}

// Enviar formulario por AJAX
document.getElementById('formColaboradora').addEventListener('submit', function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    fetch('/colaboradoras/registrar', {
        method: 'POST',
        body: formData
    })
    .then(resp => resp.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                title: '¡Registrada!',
                text: 'La colaboradora fue agregada exitosamente.',
                icon: 'success',
                confirmButtonText: 'OK',
                confirmButtonColor: '#a78bfa'  // lavanda o tono suave para spa
            }).then(() => {
                location.reload();
            });
        } else {
            Swal.fire({
                title: 'Error',
                text: 'No se pudo registrar la colaboradora.',
                icon: 'error',
                confirmButtonColor: '#f87171'
            });
        }
    });
});