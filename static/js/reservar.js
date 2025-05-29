document.addEventListener('DOMContentLoaded', () => {
    const especialidadSelect = document.getElementById('especialidad');
    const colaboradoraSelect = document.getElementById('colaboradora');
    const fechaInput = document.getElementById('fecha');
    const horaSelect = document.getElementById('hora');

    // Cargar colaboradoras al seleccionar especialidad
    especialidadSelect.addEventListener('change', () => {
        const espId = especialidadSelect.value;
        colaboradoraSelect.innerHTML = '<option value="">Selecciona colaboradora</option>';
        horaSelect.innerHTML = '<option value="">Selecciona hora</option>';
        fechaInput.value = '';

        if (!espId) return;

        fetch(`/api/colaboradoras/${espId}`)
            .then(res => res.json())
            .then(data => {
                data.forEach(c => {
                    const option = document.createElement('option');
                    option.value = c.id;
                    option.textContent = c.nombre;
                    colaboradoraSelect.appendChild(option);
                });
            })
            .catch(console.error);
    });

    // Cargar horarios al cambiar colaboradora o fecha
    function cargarHorarios() {
        const colId = colaboradoraSelect.value;
        const fecha = fechaInput.value;
        horaSelect.innerHTML = '<option value="">Selecciona hora</option>';

        if (!colId || !fecha) return;

        fetch(`/api/disponibilidad/${colId}/${fecha}`)
            .then(res => res.json())
            .then(data => {
                if (data.length === 0) {
                    const option = document.createElement('option');
                    option.textContent = 'No hay horarios disponibles';
                    option.disabled = true;
                    horaSelect.appendChild(option);
                    return;
                }
                data.forEach(hora => {
                    const option = document.createElement('option');
                    option.value = hora;
                    option.textContent = hora;
                    horaSelect.appendChild(option);
                });
            })
            .catch(console.error);
    }

    colaboradoraSelect.addEventListener('change', cargarHorarios);
    fechaInput.addEventListener('change', cargarHorarios);
});
