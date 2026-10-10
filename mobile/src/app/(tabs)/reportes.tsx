import { EstadoVacio } from '../../components/EstadoVacio';
import { Pantalla } from '../../components/Pantalla';
import { Tarjeta } from '../../components/Tarjeta';

export default function Reportes() {
  return (
    <Pantalla titulo="Reportes" subtitulo="Lo que has enviado">
      <Tarjeta>
        <EstadoVacio
          icono="document-text-outline"
          titulo="Aún no tienes reportes"
          descripcion="Cuando envíes una foto, aparecerá aquí con su estado."
        />
      </Tarjeta>
    </Pantalla>
  );
}
