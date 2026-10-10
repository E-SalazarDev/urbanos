import { EstadoVacio } from '../../components/EstadoVacio';
import { Boton } from '../../components/Boton';
import { Pantalla } from '../../components/Pantalla';
import { Tarjeta } from '../../components/Tarjeta';

export default function Capturar() {
  return (
    <Pantalla titulo="Capturar" subtitulo="Foto del daño con tu ubicación">
      <Tarjeta>
        <EstadoVacio
          icono="camera-outline"
          titulo="Foto con ubicación"
          descripcion="Aquí tomarás la foto del daño y guardaremos dónde estás. Se activa en el siguiente paso."
        />
        <Boton texto="Tomar foto" icono="camera" deshabilitado />
      </Tarjeta>
    </Pantalla>
  );
}
