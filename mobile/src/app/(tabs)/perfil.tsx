import { EstadoVacio } from '../../components/EstadoVacio';
import { Pantalla } from '../../components/Pantalla';
import { Tarjeta } from '../../components/Tarjeta';
import { Texto } from '../../components/Texto';

export default function Perfil() {
  return (
    <Pantalla titulo="Perfil" subtitulo="Tu cuenta y ajustes">
      <Tarjeta>
        <EstadoVacio
          icono="person-outline"
          titulo="Inicio de sesión pendiente"
          descripcion="Las cuentas y los roles llegan más adelante."
        />
      </Tarjeta>
      <Tarjeta>
        <Texto variante="cuerpoFuerte">Apariencia</Texto>
        <Texto variante="pequeno" suave>
          Automática: sigue el modo claro u oscuro de tu teléfono.
        </Texto>
      </Tarjeta>
    </Pantalla>
  );
}
