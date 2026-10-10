import { StyleSheet, View } from 'react-native';

import { EstadoVacio } from '../../components/EstadoVacio';
import { Insignia } from '../../components/Insignia';
import { Pantalla } from '../../components/Pantalla';
import { Tarjeta } from '../../components/Tarjeta';
import { Texto } from '../../components/Texto';
import { ESTADOS_TRAMO } from '../../constants/danos';
import { espacio } from '../../theme';

export default function Mapa() {
  return (
    <Pantalla titulo="Mapa" subtitulo="Deterioro de las calles">
      <Tarjeta>
        <EstadoVacio
          icono="map-outline"
          titulo="El mapa llega pronto"
          descripcion="Aquí verás las detecciones y el estado de cada tramo de calle."
        />
      </Tarjeta>

      <Tarjeta>
        <Texto variante="subtitulo">Cómo leer el mapa</Texto>
        <View style={estilos.fila}>
          {Object.entries(ESTADOS_TRAMO).map(([clave, e]) => (
            <Insignia key={clave} texto={e.nombre} icono={e.icono} color={e.color} />
          ))}
        </View>
      </Tarjeta>
    </Pantalla>
  );
}

const estilos = StyleSheet.create({
  fila: { flexDirection: 'row', flexWrap: 'wrap', gap: espacio.sm },
});
