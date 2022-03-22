var socket = new WebSocket(
  'ws://'+
  'ietivroom.herokuapp.com/'+
  'ws/entrega/'
);

socket.onmessage = function(e) {
  const data = JSON.parse(e.data);
  console.log(`entrega con id=${data.id} ha sido editada`)
  document.getElementById("diana").value = data.id

  $.ajax({url:'/api/entrega/'+data.id,success:(res)=>{
    $('.js-nota').val(res.data[0].nota)
    console.log(res.data[0].nota);
  }})

}



const app = Vue.createApp({
  delimiters: ['[[', ']]'],
  data() {
      return {
          id_entrega_cambiada: '',

          id_entrega: '',
          id_ejercicio: '',

          curso: '',
          ejercicio: '',
          enunciado: '',
          tipo_ejercicio: '',
          icono_ejercicio: '',
          nombre: '',
          correo: '',
          archivo: '',
          comentario_alumno: '',
          comentario_profesor: '',
          fecha_publicacion: '',
          fecha_edicion: '',
          nota: '',
          nota_maxima: '',
          enviar_notificacion: false
      };
  },
  watch: {

    id_entrega: {
      handler(id) {
        this.get_data(id);
      }
    },

    id_entrega_cambiada: {
      handler(value) {
        console.log(this.params)
        
      }
      ,deep: true
    }

  },
  methods: {
    get_data(id) {
      
      fetch(`/api/entrega/${id}`, {method: 'GET'})
        .then(response => response.json())
        .then((result) => {
          let entrega = result.data[0];

          this.archivo = '/'+entrega.archivo;
          this.comentario_alumno = entrega.comentario_alumno;
          this.comentario_profesor = entrega.comentario_profesor;
          this.fecha_publicacion = entrega.fecha_publicacion;
          this.fecha_edicion = entrega.fecha_edicion;
          this.nota = entrega.nota;

          fetch(`/api/usuario/${entrega.autor_id}`, {method: 'GET'})
            .then(response => response.json())
            .then((result) => {
              let usuario = result.data[0];

              this.nombre = `${usuario.first_name} ${usuario.last_name}`;
              this.correo = usuario.email;

            });

          fetch(`/api/ejercicio/${entrega.ejercicio_id}`, {method: 'GET'})
            .then(response => response.json())
            .then((result) => {
              let ejercicio = result.data[0];

              this.ejercicio = ejercicio.titulo;
              this.enunciado = ejercicio.enunciado;
              this.id_ejercicio = ejercicio.id;
              this.nota_maxima = ejercicio.nota_maxima;

              fetch(`/api/tipo_ejercicio/${ejercicio.tipo_ejercicio_id}`, {method: 'GET'})
                .then(response => response.json())
                .then((result) => {
                  let tipo_ejercicio = result.data[0];

                  this.tipo_ejercicio = tipo_ejercicio.nombre;
                  this.icono_ejercicio = '/'+tipo_ejercicio.icono;
                })

              fetch(`/api/curso/${ejercicio.curso_id}`, {method: 'GET'})
                .then(response => response.json())
                .then((result) => {
                  let curso = result.data[0];

                  this.curso = curso.titulo;

                })

            })

        })
        .catch(error => console.log('error', error));
    },

    set_entrega(id_entrega) {
      this.id_entrega = id_entrega;
    },

    update_entrega() {
      console.log("update_entrega called")
      if (this.id_entrega == this.entrega_cambiada) {
        console.log("recargando")
        this.get_data(id_entrega);
      }
      this.entrega_cambiada = '';
    },

    set_siguiente() {
      fetch(`/api/entregas/${this.id_ejercicio}`, {method: 'GET'})
        .then(response => response.json())
        .then((result) => {
          let entregas = result.data;
          entregas.sort( (a, b) => a.id > b.id );

          let siguiente_id;
          for (var i = 0; i < entregas.length - 1; i++){
            if (entregas[i].id == this.id_entrega){
              siguiente_id = entregas[i+1].id; 
              break;
            }
          }
          if (!siguiente_id) {
            siguiente_id = entregas[0].id;
          }

          this.set_entrega(siguiente_id);
        })
        .catch(error => console.log('error', error));
    },

    set_anterior() {
      fetch(`/api/entregas/${this.id_ejercicio}`, {method: 'GET'})
        .then(response => response.json())
        .then((result) => {
          let entregas = result.data;
          entregas.sort( (a, b) => a.id > b.id );

          let anterior_id;
          for (var i = entregas.length -1; i > 0; i--){
            if (entregas[i].id == this.id_entrega){
              anterior_id = entregas[i-1].id; 
              break;
            }
          }
          if (!anterior_id) {
            anterior_id = entregas[entregas.length-1].id;
          }

          this.set_entrega(anterior_id);
        })
        .catch(error => console.log('error', error));
    },

    save_nota_and_comment() {

      var myHeaders = new Headers();
      myHeaders.append("Content-Type", "application/json");

      var raw = JSON.stringify({
        "new_note": this.nota,
        "comment_prof": this.comentario_profesor
      });

      var requestOptions = {
        method: 'PUT',
        headers: myHeaders,
        body: raw      
      };

      fetch(`/api/entrega/${this.id_entrega}`, requestOptions)
        .then(respuesta => respuesta.text())
        .then((mensage) => {
          alert(mensage);
          socket.send(JSON.stringify({
              'id': this.id_entrega
          }))
        })
        .catch(error => console.log(error));

    }
    

  },
  mounted() {
    this.set_entrega(1);
  }
});
app.mount('#app');
